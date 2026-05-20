#!/usr/bin/env python3
"""
Quick TanStack Attack Scanner
Efficiently scans for TanStack and related Mini Shai-Hulud compromised packages
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Set

class TanStackScanner:
    def __init__(self, token=None):
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers.update({'Authorization': f'token {token}'})
        self.session.headers.update({'Accept': 'application/vnd.github.v3+json'})

        # Load compromised packages
        with open('scripts/compromised_packages.json', 'r') as f:
            data = json.load(f)
            self.attacks = data['attacks']

        # Build list of all compromised package names
        self.compromised_packages = set()
        for attack in self.attacks:
            if attack['ecosystem'] == 'npm':
                if 'package_name' in attack:
                    self.compromised_packages.add(attack['package_name'])
                elif 'packages' in attack:
                    self.compromised_packages.update(attack['packages'].keys())

        print(f"Loaded {len(self.compromised_packages)} compromised package names")

        # Known high-risk packages from TanStack attack
        self.high_priority = [
            '@tanstack/react-router',
            '@tanstack/router-core',
            '@mistralai/mistralai',
            '@uipath/cli'
        ]

        self.api_base = 'https://api.github.com'

    def search_code(self, query: str, org: str = None) -> List[Dict]:
        """Search GitHub code for specific packages"""
        results = []

        # Build search query
        search_query = f'"{query}" language:json'
        if org:
            search_query += f' org:{org}'

        print(f"  Searching for: {query}...")

        url = f'{self.api_base}/search/code'
        params = {
            'q': search_query,
            'per_page': 100
        }

        try:
            resp = self.session.get(url, params=params)

            if resp.status_code == 403:
                print(f"    Rate limited!")
                return []
            elif resp.status_code != 200:
                print(f"    Error: {resp.status_code}")
                return []

            data = resp.json()
            total = data.get('total_count', 0)
            items = data.get('items', [])

            print(f"    Found {total} results")

            for item in items:
                results.append({
                    'repo': item['repository']['full_name'],
                    'path': item['path'],
                    'url': item['html_url']
                })

            time.sleep(2)  # Rate limiting for search API

        except Exception as e:
            print(f"    Error searching: {e}")

        return results

    def quick_scan_org(self, org: str) -> Dict:
        """Quick scan using code search API"""
        print(f"\nScanning {org} for TanStack attack packages...")
        print("="*60)

        findings = {}

        # Search for high-priority packages only
        for pkg in self.high_priority:
            results = self.search_code(pkg, org)
            if results:
                findings[pkg] = results

        return findings

    def scan_all_orgs(self, orgs: List[str]) -> Dict:
        """Scan all organizations"""
        all_findings = {}

        for org in orgs:
            findings = self.quick_scan_org(org)
            if findings:
                all_findings[org] = findings
            else:
                all_findings[org] = "clean"

        return all_findings

def main():
    print("TanStack/Mini Shai-Hulud Attack Scanner")
    print(f"Started: {datetime.now().isoformat()}")
    print("="*60)

    # Check for token
    token = None
    try:
        with open('.github_token', 'r') as f:
            token = f.read().strip()
            print("Using GitHub token")
    except:
        print("WARNING: No GitHub token - code search requires authentication!")
        print("Code search API requires authentication, exiting...")
        return

    scanner = TanStackScanner(token)

    # SUSE organizations (loaded from scan_targets.json)
    with open('scripts/scan_targets.json', 'r') as f:
        targets = json.load(f)
    orgs = [o['name'] for o in targets['github']['orgs']]

    results = scanner.scan_all_orgs(orgs)

    # Save results
    output_file = f'reports/tanstack_scan_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w') as f:
        json.dump({
            'scan_date': datetime.now().isoformat(),
            'attack': 'TanStack/Mini Shai-Hulud',
            'orgs_scanned': orgs,
            'results': results
        }, f, indent=2)

    print(f"\n\nResults saved to {output_file}")

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    total_findings = sum(len(f) for org_findings in results.values() if isinstance(org_findings, dict) for f in org_findings.values())

    if total_findings == 0:
        print("✓ No compromised packages found in SUSE repositories")
    else:
        print(f"⚠️  {total_findings} potential matches found")
        print("Manual verification required:")
        for org, org_findings in results.items():
            if isinstance(org_findings, dict):
                for pkg, locations in org_findings.items():
                    print(f"\n{org} - {pkg}:")
                    for loc in locations:
                        print(f"  - {loc['repo']}: {loc['path']}")

if __name__ == '__main__':
    main()
