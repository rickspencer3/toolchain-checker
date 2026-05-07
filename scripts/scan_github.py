#!/usr/bin/env python3
"""
GitHub Repository Scanner for Supply Chain Attacks
Scans SUSE/Rancher/openSUSE GitHub repositories for compromised packages
"""

import json
import requests
import time
import sys
from typing import Dict, List, Set
from datetime import datetime

class GitHubScanner:
    def __init__(self, token=None):
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers.update({'Authorization': f'token {token}'})
        self.session.headers.update({'Accept': 'application/vnd.github.v3+json'})

        # Load compromised packages
        with open('scripts/compromised_packages.json', 'r') as f:
            data = json.load(f)
            self.compromised = data['attacks']
            # Get earliest attack date for time filtering
            attack_dates = [datetime.strptime(a['discovered'], '%Y-%m-%d') for a in data['attacks']]
            self.attack_start_date = min(attack_dates)

        # GitHub API base URL
        self.api_base = 'https://api.github.com'

        # Relevant languages for npm/PyPI attacks
        self.relevant_languages = ['JavaScript', 'TypeScript', 'Python']

    def check_rate_limit(self):
        """Check GitHub API rate limit"""
        resp = self.session.get(f'{self.api_base}/rate_limit')
        if resp.status_code == 200:
            data = resp.json()
            remaining = data['resources']['core']['remaining']
            limit = data['resources']['core']['limit']
            print(f"Rate limit: {remaining}/{limit} remaining")
            return remaining
        return 0

    def get_org_repos(self, org_name: str) -> List[Dict]:
        """Get all repositories for an organization"""
        repos = []
        page = 1
        per_page = 100

        print(f"Fetching repositories for {org_name}...")

        while True:
            url = f'{self.api_base}/orgs/{org_name}/repos'
            params = {'page': page, 'per_page': per_page, 'type': 'all'}

            resp = self.session.get(url, params=params)

            if resp.status_code == 403:
                print(f"Rate limited! Waiting...")
                time.sleep(60)
                continue
            elif resp.status_code != 200:
                print(f"Error fetching repos for {org_name}: {resp.status_code}")
                break

            data = resp.json()
            if not data:
                break

            repos.extend(data)
            print(f"  Fetched page {page} ({len(data)} repos)")

            if len(data) < per_page:
                break

            page += 1
            time.sleep(0.5)  # Be nice to the API

        print(f"Total repos for {org_name}: {len(repos)}")
        return repos

    def filter_relevant_repos(self, repos: List[Dict]) -> List[Dict]:
        """Filter repositories by language and update time"""
        relevant = []

        for repo in repos:
            # Check language (JavaScript/TypeScript for npm, Python for PyPI)
            language = repo.get('language')
            if language not in self.relevant_languages:
                continue

            # Check update time (only repos updated since attack date)
            updated_at = repo.get('updated_at')
            if updated_at:
                try:
                    # Parse GitHub's ISO 8601 format: "2026-04-23T12:00:00Z"
                    update_date = datetime.strptime(updated_at, '%Y-%m-%dT%H:%M:%SZ')
                    if update_date.date() < self.attack_start_date.date():
                        continue
                except:
                    pass  # If we can't parse the date, include it to be safe

            relevant.append(repo)

        return relevant

    def check_file_exists(self, owner: str, repo: str, path: str, branch: str = None) -> bool:
        """Check if a file exists in a repository"""
        url = f'{self.api_base}/repos/{owner}/{repo}/contents/{path}'
        params = {}
        if branch:
            params['ref'] = branch

        resp = self.session.get(url, params=params)
        return resp.status_code == 200

    def get_file_content(self, owner: str, repo: str, path: str, branch: str = None) -> str:
        """Get file content from repository"""
        url = f'{self.api_base}/repos/{owner}/{repo}/contents/{path}'
        params = {}
        if branch:
            params['ref'] = branch

        resp = self.session.get(url, params=params)

        if resp.status_code == 200:
            import base64
            content = resp.json().get('content', '')
            return base64.b64decode(content).decode('utf-8', errors='ignore')
        return None

    def get_branches(self, owner: str, repo: str) -> List[str]:
        """Get all branches for a repository"""
        branches = []
        page = 1
        per_page = 100

        while True:
            url = f'{self.api_base}/repos/{owner}/{repo}/branches'
            params = {'page': page, 'per_page': per_page}

            resp = self.session.get(url, params=params)

            if resp.status_code != 200:
                break

            data = resp.json()
            if not data:
                break

            branches.extend([b['name'] for b in data])

            if len(data) < per_page:
                break

            page += 1
            time.sleep(0.3)

        return branches

    def check_npm_package(self, content: str) -> List[Dict]:
        """Check package.json or package-lock.json for compromised npm packages"""
        findings = []

        try:
            data = json.loads(content)

            # Check dependencies
            for dep_type in ['dependencies', 'devDependencies', 'peerDependencies', 'optionalDependencies']:
                if dep_type in data:
                    for pkg_name, version in data[dep_type].items():
                        for attack in self.compromised:
                            if attack['ecosystem'] == 'npm' and attack['package_name'] == pkg_name:
                                # Check if version matches malicious versions
                                for mal_ver in attack['malicious_versions']:
                                    if mal_ver in str(version):
                                        findings.append({
                                            'package': pkg_name,
                                            'version': version,
                                            'malicious_version': mal_ver,
                                            'attack': attack
                                        })
        except:
            pass

        return findings

    def check_python_requirements(self, content: str) -> List[Dict]:
        """Check requirements.txt for compromised PyPI packages"""
        findings = []

        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Parse package name and version
            for attack in self.compromised:
                if attack['ecosystem'] == 'pypi':
                    pkg_name = attack['package_name']
                    if pkg_name.lower() in line.lower():
                        for mal_ver in attack['malicious_versions']:
                            if mal_ver in line:
                                findings.append({
                                    'package': pkg_name,
                                    'line': line,
                                    'malicious_version': mal_ver,
                                    'attack': attack
                                })

        return findings

    def scan_repository(self, owner: str, repo_name: str, branches: List[str] = None) -> Dict:
        """Scan a repository for compromised packages"""
        result = {
            'repo': f'{owner}/{repo_name}',
            'branches_checked': [],
            'findings': [],
            'status': 'clean'
        }

        # Get branches if not provided
        if branches is None:
            branches = self.get_branches(owner, repo_name)
            if not branches:
                branches = ['main', 'master']  # fallback to common default branches

        # Limit to first 10 branches to avoid excessive API calls
        branches_to_check = branches[:10]

        for branch in branches_to_check:
            result['branches_checked'].append(branch)

            # Check for package.json (npm)
            if self.check_file_exists(owner, repo_name, 'package.json', branch):
                content = self.get_file_content(owner, repo_name, 'package.json', branch)
                if content:
                    findings = self.check_npm_package(content)
                    if findings:
                        for f in findings:
                            f['file'] = 'package.json'
                            f['branch'] = branch
                        result['findings'].extend(findings)

            # Check for package-lock.json
            if self.check_file_exists(owner, repo_name, 'package-lock.json', branch):
                content = self.get_file_content(owner, repo_name, 'package-lock.json', branch)
                if content:
                    findings = self.check_npm_package(content)
                    if findings:
                        for f in findings:
                            f['file'] = 'package-lock.json'
                            f['branch'] = branch
                        result['findings'].extend(findings)

            # Check for requirements.txt (Python)
            if self.check_file_exists(owner, repo_name, 'requirements.txt', branch):
                content = self.get_file_content(owner, repo_name, 'requirements.txt', branch)
                if content:
                    findings = self.check_python_requirements(content)
                    if findings:
                        for f in findings:
                            f['file'] = 'requirements.txt'
                            f['branch'] = branch
                        result['findings'].extend(findings)

            time.sleep(0.5)  # Rate limiting

        if result['findings']:
            result['status'] = 'COMPROMISED'

        return result

    def scan_organization(self, org_name: str) -> List[Dict]:
        """Scan all repositories in an organization"""
        print(f"\n{'='*60}")
        print(f"Scanning organization: {org_name}")
        print(f"{'='*60}\n")

        all_repos = self.get_org_repos(org_name)

        # Filter to relevant repos (by language and update time)
        print(f"Filtering repositories...")
        print(f"  Attack start date: {self.attack_start_date.strftime('%Y-%m-%d')}")
        print(f"  Relevant languages: {', '.join(self.relevant_languages)}")

        repos = self.filter_relevant_repos(all_repos)

        print(f"  Total repos: {len(all_repos)}")
        print(f"  Relevant repos (updated since {self.attack_start_date.strftime('%Y-%m-%d')} with JS/TS/Python): {len(repos)}")
        print()

        results = []

        for i, repo in enumerate(repos, 1):
            print(f"[{i}/{len(repos)}] Scanning {repo['full_name']} ({repo.get('language', 'unknown')})...", end=' ')

            result = self.scan_repository(repo['owner']['login'], repo['name'])
            results.append(result)

            if result['status'] == 'COMPROMISED':
                print(f"⚠️  COMPROMISED! ({len(result['findings'])} findings)")
            else:
                print(f"✓")

            # Check rate limit every 10 repos
            if i % 10 == 0:
                remaining = self.check_rate_limit()
                if remaining < 100:
                    print(f"Low rate limit ({remaining}), waiting 60 seconds...")
                    time.sleep(60)

        return results

def main():
    print(f"GitHub Scanner for Supply Chain Attacks")
    print(f"Started at: {datetime.now().isoformat()}")
    print(f"=" * 60)

    # Check for GitHub token
    token = None
    try:
        with open('.github_token', 'r') as f:
            token = f.read().strip()
            print("Using GitHub token from .github_token file")
    except:
        print("No GitHub token found - running with rate limit of 60 req/hour")

    scanner = GitHubScanner(token)
    scanner.check_rate_limit()

    # Organizations to scan
    orgs = ['SUSE', 'rancher', 'SUSE-Rancher-Community', 'rancher-sandbox', 'openSUSE']

    # Create output filename at start
    output_file = f'reports/github_scan_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    all_results = {}

    for org in orgs:
        try:
            results = scanner.scan_organization(org)
            all_results[org] = results
        except Exception as e:
            print(f"Error scanning {org}: {e}")
            all_results[org] = {'error': str(e)}

        # Save results after each org (incremental updates)
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"Progress saved to {output_file}")

    print(f"\n{'='*60}")
    print(f"Scan complete! Results saved to {output_file}")
    print(f"Finished at: {datetime.now().isoformat()}")

if __name__ == '__main__':
    main()
