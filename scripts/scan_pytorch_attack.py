#!/usr/bin/env python3
"""
PyTorch Lightning Supply Chain Attack Scanner
Scans for:
1. pytorch-lightning 2.6.2 or 2.6.3 in requirements.txt
2. Malicious persistence hooks in .claude/ and .vscode/ directories
"""

import json
import requests
import time
import sys
from typing import Dict, List, Set
from datetime import datetime
import base64

class PyTorchAttackScanner:
    def __init__(self, token=None):
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers.update({'Authorization': f'token {token}'})
        self.session.headers.update({'Accept': 'application/vnd.github.v3+json'})

        self.api_base = 'https://api.github.com'

        # Define SUSE AI repos to prioritize
        self.ai_repos = [
            'SUSE/suse-ai-stack',
            'SUSE/suse-ai-observability-extension',
            'SUSE/doc-suse-ai',
            'SUSE/suse-ai-up',
            'SUSE/suse-ai-deployer'
        ]

        # Define all orgs to scan
        self.orgs = ['SUSE', 'rancher', 'rancher-sandbox', 'openSUSE', 'SUSE-Rancher-Community']

        # Results tracking
        self.results = {
            'scan_timestamp': datetime.now().isoformat(),
            'attack': 'pytorch-lightning 2.6.2, 2.6.3',
            'ai_repos_scanned': [],
            'ai_repos_affected': [],
            'general_repos_scanned': [],
            'general_repos_affected': [],
            'persistence_hooks_found': [],
            'total_repos_checked': 0,
            'total_affected': 0
        }

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

    def get_file_content(self, repo_full_name: str, file_path: str, branch: str = 'main') -> str:
        """Get content of a file from a repository"""
        url = f'{self.api_base}/repos/{repo_full_name}/contents/{file_path}'
        params = {'ref': branch}

        for attempt in range(3):
            resp = self.session.get(url, params=params)

            if resp.status_code == 403:
                print(f"  Rate limited, waiting...")
                time.sleep(60)
                continue
            elif resp.status_code == 404:
                return None  # File doesn't exist
            elif resp.status_code != 200:
                print(f"  Error fetching {file_path}: {resp.status_code}")
                return None

            data = resp.json()
            if data.get('encoding') == 'base64':
                content = base64.b64decode(data['content']).decode('utf-8', errors='ignore')
                return content

            return None

        return None

    def get_directory_contents(self, repo_full_name: str, dir_path: str, branch: str = 'main') -> List[Dict]:
        """Get contents of a directory"""
        url = f'{self.api_base}/repos/{repo_full_name}/contents/{dir_path}'
        params = {'ref': branch}

        resp = self.session.get(url, params=params)

        if resp.status_code == 404:
            return []  # Directory doesn't exist
        elif resp.status_code != 200:
            return []

        return resp.json()

    def check_requirements_file(self, content: str) -> bool:
        """Check if requirements.txt contains malicious pytorch-lightning versions"""
        if not content:
            return False

        for line in content.split('\n'):
            line = line.strip().lower()
            if 'pytorch-lightning' in line or 'lightning' in line:
                # Check for version 2.6.2 or 2.6.3
                if '2.6.2' in line or '2.6.3' in line:
                    return True
                # Also check for unpinned versions that might pull malicious version
                if '==' not in line and '>=' not in line and '<=' not in line:
                    print(f"    WARNING: Unpinned pytorch-lightning/lightning package found")

        return False

    def check_persistence_hooks(self, repo_full_name: str, branch: str = 'main') -> List[str]:
        """Check for malicious persistence hooks in .claude/ and .vscode/"""
        suspicious_files = []

        # Check .claude/ directory
        claude_contents = self.get_directory_contents(repo_full_name, '.claude', branch)
        for item in claude_contents:
            if item['type'] == 'file':
                # Suspicious files in .claude/ that shouldn't be there
                if item['name'] not in ['settings.json', 'settings.local.json', 'keybindings.json', 'scheduled_tasks.json']:
                    suspicious_files.append(f".claude/{item['name']}")

        # Check .vscode/ directory
        vscode_contents = self.get_directory_contents(repo_full_name, '.vscode', branch)
        for item in vscode_contents:
            if item['type'] == 'file':
                # Common legitimate files
                legitimate = ['settings.json', 'launch.json', 'tasks.json', 'extensions.json']
                if item['name'] not in legitimate and not item['name'].endswith('.code-workspace'):
                    suspicious_files.append(f".vscode/{item['name']}")

        return suspicious_files

    def get_repo_branches(self, repo_full_name: str) -> List[str]:
        """Get all branches for a repository"""
        url = f'{self.api_base}/repos/{repo_full_name}/branches'

        resp = self.session.get(url)
        if resp.status_code != 200:
            return ['main']  # Default to main branch

        branches = resp.json()
        branch_names = [b['name'] for b in branches]

        # Prioritize common default branches
        priority_branches = ['main', 'master', 'develop']
        other_branches = [b for b in branch_names if b not in priority_branches]

        # Return priority branches first, then others (limit to 5 total)
        result = [b for b in priority_branches if b in branch_names] + other_branches
        return result[:5]

    def scan_repo(self, repo_full_name: str, is_ai_repo: bool = False) -> Dict:
        """Scan a single repository for pytorch-lightning attack"""
        print(f"\n{'='*60}")
        print(f"Scanning: {repo_full_name}")
        print(f"{'='*60}")

        repo_result = {
            'repo': repo_full_name,
            'is_ai_repo': is_ai_repo,
            'affected': False,
            'branches_checked': [],
            'malicious_versions_found': [],
            'persistence_hooks_found': [],
            'details': []
        }

        # Get branches
        branches = self.get_repo_branches(repo_full_name)
        print(f"Branches to check: {', '.join(branches)}")

        for branch in branches:
            print(f"\n  Checking branch: {branch}")
            repo_result['branches_checked'].append(branch)

            # Check requirements.txt
            requirements_content = self.get_file_content(repo_full_name, 'requirements.txt', branch)
            if requirements_content:
                print(f"    Found requirements.txt")
                if self.check_requirements_file(requirements_content):
                    print(f"    🚨 MALICIOUS VERSION FOUND in requirements.txt")
                    repo_result['affected'] = True
                    repo_result['malicious_versions_found'].append(f"{branch}/requirements.txt")
                    repo_result['details'].append(f"Branch {branch}: requirements.txt contains pytorch-lightning 2.6.2 or 2.6.3")

            # Check for requirements files in subdirectories (common in monorepos)
            # Skip this for now to avoid too many API calls

            # Check for persistence hooks
            print(f"    Checking for persistence hooks...")
            hooks = self.check_persistence_hooks(repo_full_name, branch)
            if hooks:
                print(f"    🚨 SUSPICIOUS PERSISTENCE HOOKS FOUND: {', '.join(hooks)}")
                repo_result['affected'] = True
                repo_result['persistence_hooks_found'].extend(hooks)
                repo_result['details'].append(f"Branch {branch}: Suspicious files in .claude/ or .vscode/: {', '.join(hooks)}")

            time.sleep(0.5)  # Be nice to the API

        if not repo_result['affected']:
            print(f"✅ CLEAN: No malicious versions or hooks found")

        # Save incremental results
        self.save_results()

        return repo_result

    def get_org_repos(self, org_name: str) -> List[str]:
        """Get all Python repositories for an organization (updated since attack date)"""
        repos = []
        page = 1
        per_page = 100

        print(f"\n{'='*60}")
        print(f"Fetching Python repositories for {org_name}...")
        print(f"{'='*60}")

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

            # Filter for Python repos updated since attack date (April 30, 2026)
            attack_date = datetime(2026, 4, 30)
            for repo in data:
                if repo.get('language') == 'Python':
                    updated_at = repo.get('updated_at')
                    if updated_at:
                        update_date = datetime.strptime(updated_at, '%Y-%m-%dT%H:%M:%SZ')
                        if update_date >= attack_date:
                            repos.append(repo['full_name'])

            print(f"  Fetched page {page} ({len(data)} repos, {len([r for r in data if r.get('language') == 'Python'])} Python)")

            if len(data) < per_page:
                break

            page += 1
            time.sleep(0.5)

        print(f"Python repos updated since attack: {len(repos)}")
        return repos

    def scan_all(self):
        """Scan all repositories"""
        print(f"\n{'*'*60}")
        print(f"PyTorch Lightning Attack Scanner")
        print(f"Attack: pytorch-lightning 2.6.2, 2.6.3 (April 30, 2026)")
        print(f"{'*'*60}")

        # Check rate limit first
        self.check_rate_limit()

        # 1. Scan priority AI repos first
        print(f"\n\n{'#'*60}")
        print(f"PHASE 1: Scanning SUSE AI Repositories (Priority)")
        print(f"{'#'*60}")

        for repo_name in self.ai_repos:
            result = self.scan_repo(repo_name, is_ai_repo=True)
            self.results['ai_repos_scanned'].append(repo_name)
            if result['affected']:
                self.results['ai_repos_affected'].append(result)
                self.results['total_affected'] += 1
            self.results['total_repos_checked'] += 1

        # 2. Scan all Python repos in SUSE orgs
        print(f"\n\n{'#'*60}")
        print(f"PHASE 2: Scanning All Python Repositories")
        print(f"{'#'*60}")

        for org in self.orgs:
            repo_list = self.get_org_repos(org)

            for repo_name in repo_list:
                # Skip AI repos we already scanned
                if repo_name in self.ai_repos:
                    continue

                result = self.scan_repo(repo_name, is_ai_repo=False)
                self.results['general_repos_scanned'].append(repo_name)
                if result['affected']:
                    self.results['general_repos_affected'].append(result)
                    self.results['total_affected'] += 1
                self.results['total_repos_checked'] += 1

        # Save final results
        self.save_results()
        self.print_summary()

    def save_results(self):
        """Save scan results to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'reports/pytorch_attack_scan_{timestamp}.json'

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n[Results saved to {output_file}]")

    def print_summary(self):
        """Print scan summary"""
        print(f"\n\n{'='*60}")
        print(f"SCAN SUMMARY")
        print(f"{'='*60}")
        print(f"Total repositories checked: {self.results['total_repos_checked']}")
        print(f"AI repositories checked: {len(self.results['ai_repos_scanned'])}")
        print(f"General repositories checked: {len(self.results['general_repos_scanned'])}")
        print(f"\nAFFECTED REPOSITORIES: {self.results['total_affected']}")

        if self.results['ai_repos_affected']:
            print(f"\n🚨 CRITICAL: AI Repos Affected:")
            for result in self.results['ai_repos_affected']:
                print(f"  - {result['repo']}")
                for detail in result['details']:
                    print(f"      {detail}")

        if self.results['general_repos_affected']:
            print(f"\n🚨 WARNING: General Repos Affected:")
            for result in self.results['general_repos_affected']:
                print(f"  - {result['repo']}")
                for detail in result['details']:
                    print(f"      {detail}")

        if self.results['total_affected'] == 0:
            print(f"\n✅ ALL CLEAR: No malicious pytorch-lightning versions or persistence hooks found")

        print(f"{'='*60}\n")

def main():
    # Load GitHub token
    try:
        with open('.github_token', 'r') as f:
            token = f.read().strip()
    except FileNotFoundError:
        print("ERROR: .github_token file not found")
        print("GitHub token required for scanning")
        sys.exit(1)

    scanner = PyTorchAttackScanner(token=token)
    scanner.scan_all()

if __name__ == '__main__':
    main()
