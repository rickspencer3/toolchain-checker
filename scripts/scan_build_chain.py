#!/usr/bin/env python3
"""
Build Chain Scanner - Check for Bitwarden CLI in CI/CD and build infrastructure
Scans: GitHub Actions, Dockerfiles, shell scripts, subdirectory package.json
"""

import json
import requests
import base64
import time
import re
from typing import List, Dict

class BuildChainScanner:
    def __init__(self, token):
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        })
        self.api_base = 'https://api.github.com'

        # Patterns to search for
        self.bitwarden_patterns = [
            r'@bitwarden/cli',
            r'npx.*bw\s',
            r'npm.*install.*bitwarden',
            r'bw\s+login',
            r'bw\s+get',
            r'bw\s+unlock',
            r'/bw\s',  # bw binary
        ]

    def check_rate_limit(self):
        """Check and display rate limit"""
        resp = self.session.get(f'{self.api_base}/rate_limit')
        if resp.status_code == 200:
            data = resp.json()
            remaining = data['resources']['core']['remaining']
            limit = data['resources']['core']['limit']
            print(f"  Rate limit: {remaining}/{limit} remaining")
            return remaining
        return 0

    def get_file_content(self, owner: str, repo: str, path: str, ref: str = 'main') -> str:
        """Get file content from GitHub"""
        url = f'{self.api_base}/repos/{owner}/{repo}/contents/{path}?ref={ref}'
        resp = self.session.get(url)

        if resp.status_code == 200:
            content = base64.b64decode(resp.json()['content']).decode('utf-8', errors='ignore')
            return content
        return None

    def search_repo_code(self, owner: str, repo: str, query: str) -> List[Dict]:
        """Search code in a specific repository"""
        url = f'{self.api_base}/search/code?q={query}+repo:{owner}/{repo}'
        resp = self.session.get(url)

        if resp.status_code == 200:
            return resp.json().get('items', [])
        elif resp.status_code == 403:
            print(f"    Rate limited on code search, waiting 10s...")
            time.sleep(10)
            return []
        return []

    def check_content_for_bitwarden(self, content: str, file_path: str) -> List[str]:
        """Check if content contains Bitwarden patterns"""
        findings = []

        for pattern in self.bitwarden_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Get context (line containing the match)
                start = max(0, content.rfind('\n', 0, match.start()) + 1)
                end = content.find('\n', match.end())
                if end == -1:
                    end = len(content)
                line = content[start:end].strip()

                findings.append({
                    'pattern': pattern,
                    'line': line,
                    'file': file_path
                })

        return findings

    def scan_repository(self, owner: str, repo_name: str) -> Dict:
        """Scan repository build chain for Bitwarden usage"""
        result = {
            'repo': f'{owner}/{repo_name}',
            'findings': [],
            'files_checked': [],
            'status': 'clean'
        }

        print(f"\n  Scanning {owner}/{repo_name}...")

        # Files/paths to check
        check_targets = [
            # GitHub Actions
            '.github/workflows',
            # Docker
            'Dockerfile',
            '.dockerfile',
            # CI configs
            '.gitlab-ci.yml',
            '.circleci/config.yml',
            '.travis.yml',
            'azure-pipelines.yml',
            'Jenkinsfile',
            # Scripts
            'scripts',
            'build',
            '.ci',
            # Root package.json (for completeness)
            'package.json',
        ]

        # Try to get repository tree
        tree_url = f'{self.api_base}/repos/{owner}/{repo_name}/git/trees/main?recursive=1'
        resp = self.session.get(tree_url)

        if resp.status_code != 200:
            # Try master branch
            tree_url = f'{self.api_base}/repos/{owner}/{repo_name}/git/trees/master?recursive=1'
            resp = self.session.get(tree_url)

        if resp.status_code == 200:
            tree_data = resp.json()
            files = tree_data.get('tree', [])

            # Filter files we want to check
            relevant_files = []
            for file in files:
                if file['type'] != 'blob':
                    continue

                path = file['path']

                # Check if file matches our targets
                if (path.startswith('.github/workflows/') and path.endswith('.yml')) or \
                   (path.startswith('.github/workflows/') and path.endswith('.yaml')) or \
                   'Dockerfile' in path or \
                   path.endswith('.dockerfile') or \
                   path in ['.gitlab-ci.yml', '.circleci/config.yml', '.travis.yml',
                           'azure-pipelines.yml', 'Jenkinsfile'] or \
                   (path.startswith('scripts/') and (path.endswith('.sh') or path.endswith('.bash'))) or \
                   (path.startswith('.ci/') and path.endswith('.sh')) or \
                   path == 'package.json' or \
                   (path.endswith('/package.json')):
                    relevant_files.append(path)

            print(f"    Found {len(relevant_files)} relevant build/CI files")

            # Check each file
            for file_path in relevant_files[:50]:  # Limit to 50 files to avoid excessive API calls
                result['files_checked'].append(file_path)

                content = self.get_file_content(owner, repo_name, file_path)
                if content:
                    findings = self.check_content_for_bitwarden(content, file_path)
                    if findings:
                        result['findings'].extend(findings)
                        print(f"    ⚠️  FOUND in {file_path}:")
                        for f in findings:
                            print(f"       {f['line'][:80]}")

                time.sleep(0.2)  # Rate limit protection

        else:
            print(f"    Could not access repository tree (may be empty or inaccessible)")

        if result['findings']:
            result['status'] = 'bitwarden_detected'

        return result

def main():
    print("Build Chain Scanner - Checking for Bitwarden CLI Usage")
    print("=" * 70)

    # Load GitHub token
    try:
        with open('.github_token', 'r') as f:
            token = f.read().strip()
    except:
        print("Error: .github_token file not found")
        return

    scanner = BuildChainScanner(token)
    scanner.check_rate_limit()

    # Load scan results to get repo list
    with open('reports/github_scan_20260423_173753.json', 'r') as f:
        scan_data = json.load(f)

    all_results = {}
    total_repos = 0
    repos_with_bitwarden = 0

    for org, repos in scan_data.items():
        all_results[org] = []

        print(f"\n{'=' * 70}")
        print(f"Organization: {org}")
        print('=' * 70)

        for repo_info in repos:
            repo = repo_info['repo']
            owner, repo_name = repo.split('/')

            result = scanner.scan_repository(owner, repo_name)
            all_results[org].append(result)
            total_repos += 1

            if result['status'] == 'bitwarden_detected':
                repos_with_bitwarden += 1

    # Save results
    with open('reports/build_chain_scan.json', 'w') as f:
        json.dump(all_results, f, indent=2)

    # Summary
    print("\n" + "=" * 70)
    print("SCAN COMPLETE")
    print("=" * 70)
    print(f"Total repositories scanned: {total_repos}")
    print(f"Repositories with Bitwarden CLI detected: {repos_with_bitwarden}")
    print()

    if repos_with_bitwarden > 0:
        print("⚠️  BITWARDEN DETECTED in build chains:")
        for org, repos in all_results.items():
            for repo in repos:
                if repo['status'] == 'bitwarden_detected':
                    print(f"\n  {repo['repo']}:")
                    for finding in repo['findings']:
                        print(f"    File: {finding['file']}")
                        print(f"    Line: {finding['line'][:100]}")
    else:
        print("✅ No Bitwarden CLI usage detected in any build chains")

    print()
    print("Results saved to: reports/build_chain_scan.json")

if __name__ == '__main__':
    main()
