#!/usr/bin/env python3
"""
OBS Recent Updates Scanner for Supply Chain Attacks
Scans only recently updated OBS packages (last 24 hours)
"""

import json
import requests
import time
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from run_log import log, attack_label

class OBSRecentScanner:
    def __init__(self):
        self.obs_base = 'https://build.opensuse.org/public'
        self.rss_url = 'https://build.opensuse.org/main/latest_updates.rss'
        self.session = requests.Session()

        # Load compromised packages
        with open('scripts/compromised_packages.json', 'r') as f:
            data = json.load(f)
            self.compromised = data['attacks']

    def get_recent_updates(self, hours=24) -> List[Tuple[str, str]]:
        """Get packages updated in last N hours from RSS feed"""
        print(f"Fetching packages updated in last {hours} hours...")

        # The RSS feed only shows last ~100 items, but we can try multiple endpoints
        packages = set()
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        try:
            resp = self.session.get(self.rss_url)
            if resp.status_code != 200:
                print(f"Error fetching RSS feed: {resp.status_code}")
                return []

            root = ET.fromstring(resp.content)

            for item in root.findall('.//item'):
                pub_date_str = item.find('pubDate').text
                # Parse: "2026-04-23 09:57:05 UTC"
                pub_date = datetime.strptime(pub_date_str, "%Y-%m-%d %H:%M:%S %Z")

                if pub_date >= cutoff_time:
                    title = item.find('title').text
                    # Parse: "Package bootstrap-copy in project openSUSE:Factory:Staging:L updated"
                    parts = title.split(' in project ')
                    if len(parts) == 2:
                        package_name = parts[0].replace('Package ', '')
                        project_name = parts[1].replace(' updated', '')
                        packages.add((project_name, package_name))

            print(f"Found {len(packages)} packages updated in last {hours} hours")
            return list(packages)

        except Exception as e:
            print(f"Error parsing RSS feed: {e}")
            return []

    def get_package_files(self, project: str, package: str) -> List[str]:
        """Get files for a package"""
        url = f'{self.obs_base}/source/{project}/{package}'

        try:
            resp = self.session.get(url)
            if resp.status_code != 200:
                return []

            root = ET.fromstring(resp.content)
            files = [entry.get('name') for entry in root.findall('entry') if entry.get('name')]
            return files
        except:
            return []

    def get_file_content(self, project: str, package: str, filename: str) -> str:
        """Get file content from OBS"""
        url = f'{self.obs_base}/source/{project}/{package}/{filename}'

        try:
            resp = self.session.get(url)
            if resp.status_code == 200:
                return resp.text
            return None
        except:
            return None

    def check_npm_in_file(self, content: str) -> List[Dict]:
        """Check if file references compromised npm packages"""
        findings = []

        for attack in self.compromised:
            if attack['ecosystem'] != 'npm':
                continue

            # Handle single-package format (package_name + malicious_versions)
            if 'package_name' in attack:
                pkg_name = attack['package_name']
                if pkg_name in content:
                    for mal_ver in attack['malicious_versions']:
                        if mal_ver in content:
                            findings.append({
                                'package': pkg_name,
                                'version': mal_ver,
                                'attack': attack
                            })

            # Handle multi-package format (package_scope + packages dict)
            elif 'packages' in attack:
                for pkg_name, mal_versions in attack['packages'].items():
                    if pkg_name in content:
                        for mal_ver in mal_versions:
                            if mal_ver in content:
                                findings.append({
                                    'package': pkg_name,
                                    'version': mal_ver,
                                    'attack': attack
                                })

        return findings

    def check_python_in_file(self, content: str) -> List[Dict]:
        """Check if file references compromised Python packages"""
        findings = []

        for attack in self.compromised:
            if attack['ecosystem'] == 'pypi':
                pkg_name = attack['package_name']

                # Look for Python package references
                if pkg_name.lower() in content.lower():
                    for mal_ver in attack['malicious_versions']:
                        if mal_ver in content:
                            findings.append({
                                'package': pkg_name,
                                'version': mal_ver,
                                'attack': attack
                            })

        return findings

    def scan_package(self, project: str, package: str) -> Dict:
        """Scan an OBS package for compromised dependencies"""
        result = {
            'project': project,
            'package': package,
            'findings': [],
            'status': 'clean'
        }

        # Get package files
        files = self.get_package_files(project, package)

        # Check relevant files
        for filename in files:
            findings = []

            # Check spec files, package.json, requirements.txt
            if filename.endswith('.spec') or filename == 'package.json' or filename == 'requirements.txt':
                content = self.get_file_content(project, package, filename)
                if content:
                    findings.extend(self.check_npm_in_file(content))
                    findings.extend(self.check_python_in_file(content))

            if findings:
                for f in findings:
                    f['file'] = filename
                result['findings'].extend(findings)

            time.sleep(0.2)  # Be nice to the API

        if result['findings']:
            result['status'] = 'COMPROMISED'

        return result

    def scan_recent_updates(self, hours=24) -> List[Dict]:
        """Scan recently updated packages"""
        print(f"\n{'='*60}")
        print(f"OBS Recent Updates Scanner")
        print(f"Scanning packages updated in last {hours} hours")
        print(f"{'='*60}\n")

        packages = self.get_recent_updates(hours)

        if not packages:
            print("No recent updates found")
            return []

        results = []

        for i, (project, package) in enumerate(packages, 1):
            print(f"[{i}/{len(packages)}] Scanning {project}/{package}...", end=' ')

            result = self.scan_package(project, package)
            results.append(result)

            if result['status'] == 'COMPROMISED':
                print(f"⚠️  COMPROMISED!")
            else:
                print(f"✓")

            time.sleep(0.5)  # Rate limiting

        return results

def main():
    print(f"OBS Recent Updates Scanner for Supply Chain Attacks")
    print(f"Started at: {datetime.now().isoformat()}")
    print(f"=" * 60)

    log('RUN_START', 'OBS quick scan initiated (last 24h RSS feed)')

    scanner = OBSRecentScanner()

    for attack in scanner.compromised:
        log('ATTACK', attack_label(attack))

    # Create output filename at start
    output_file = f'reports/obs_recent_scan_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

    # Scan packages updated in last 24 hours
    results = scanner.scan_recent_updates(hours=24)

    # Save results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Scan complete! Scanned {len(results)} recently updated packages")

    compromised = [r for r in results if r['status'] == 'COMPROMISED']
    if compromised:
        print(f"⚠️  WARNING: {len(compromised)} compromised packages found!")
    else:
        print(f"✓ No compromised packages detected")

    print(f"Results saved to {output_file}")
    print(f"Finished at: {datetime.now().isoformat()}")

    if compromised:
        log('COMPROMISED', f"OBS quick: {len(results)} packages scanned, {len(compromised)} COMPROMISED → {output_file}")
    else:
        log('CLEAN', f"OBS quick: {len(results)} packages scanned, 0 compromised → {output_file}")

if __name__ == '__main__':
    main()
