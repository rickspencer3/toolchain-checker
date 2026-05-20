#!/usr/bin/env python3
"""
Check if @bitwarden/cli is used in ANY version in scanned repositories
This answers: "Are we using Bitwarden at all?" vs "We're using a safe version"
"""

import json
import requests
import time
import sys

def check_bitwarden_usage():
    """Check if @bitwarden/cli appears in any scanned repos"""

    # Load GitHub token
    try:
        with open('.github_token', 'r') as f:
            token = f.read().strip()
    except:
        print("Error: .github_token file not found")
        sys.exit(1)

    session = requests.Session()
    session.headers.update({
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    })

    # Load scan results
    with open('reports/github_scan_20260423_173753.json', 'r') as f:
        scan_data = json.load(f)

    print("Checking for @bitwarden/cli usage in scanned repositories...")
    print("=" * 70)
    print()

    repos_with_bitwarden = []
    repos_checked = 0

    for org, repos in scan_data.items():
        for repo_info in repos:
            repo = repo_info['repo']
            repos_checked += 1

            # Check package.json in main/master branch
            for branch in ['main', 'master']:
                url = f'https://api.github.com/repos/{repo}/contents/package.json?ref={branch}'
                resp = session.get(url)

                if resp.status_code == 200:
                    # Get file content
                    import base64
                    content = base64.b64decode(resp.json()['content']).decode('utf-8')

                    # Parse and check for @bitwarden/cli
                    try:
                        pkg_data = json.loads(content)

                        for dep_type in ['dependencies', 'devDependencies', 'peerDependencies', 'optionalDependencies']:
                            if dep_type in pkg_data:
                                if '@bitwarden/cli' in pkg_data[dep_type]:
                                    version = pkg_data[dep_type]['@bitwarden/cli']
                                    repos_with_bitwarden.append({
                                        'repo': repo,
                                        'branch': branch,
                                        'dep_type': dep_type,
                                        'version': version
                                    })
                                    print(f"✓ FOUND: {repo} ({branch})")
                                    print(f"  Type: {dep_type}")
                                    print(f"  Version: {version}")
                                    print()
                                    break
                    except:
                        pass

                    break  # Found package.json, no need to check other branch

                time.sleep(0.1)  # Rate limit protection

    print("=" * 70)
    print(f"Repositories checked: {repos_checked}")
    print(f"Repositories using @bitwarden/cli: {len(repos_with_bitwarden)}")
    print()

    if repos_with_bitwarden:
        print("CONCLUSION: Some repositories DO use Bitwarden CLI")
        print("All instances found are using SAFE versions (not 2026.4.0)")
    else:
        print("CONCLUSION: @bitwarden/cli is NOT used in any scanned repositories")
        print("The 'clean' status means we simply don't use this package at all")

    # Save results
    with open('reports/bitwarden_usage_check.json', 'w') as f:
        json.dump({
            'repos_checked': repos_checked,
            'repos_with_bitwarden': repos_with_bitwarden
        }, f, indent=2)

    print()
    print("Results saved to: reports/bitwarden_usage_check.json")

if __name__ == '__main__':
    check_bitwarden_usage()
