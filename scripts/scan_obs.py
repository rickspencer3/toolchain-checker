#!/usr/bin/env python3
"""
Comprehensive OBS Scanner for Supply Chain Attacks
Scans SUSE-responsible projects for packages updated since attack discovery
"""

import json
import requests
import time
import xml.etree.ElementTree as ET
from typing import Dict, List, Set
from datetime import datetime

class OBSComprehensiveScanner:
    def __init__(self):
        self.obs_base = 'https://build.opensuse.org/public'
        self.session = requests.Session()

        # Load compromised packages
        with open('scripts/compromised_packages.json', 'r') as f:
            data = json.load(f)
            self.compromised = data['attacks']
            # Get earliest attack date
            attack_dates = [datetime.strptime(a['discovered'], '%Y-%m-%d') for a in data['attacks']]
            self.attack_start_date = min(attack_dates)

        # SUSE-responsible projects (official SUSE/openSUSE projects)
        self.suse_projects = [
            'openSUSE:Factory',
            'openSUSE:Leap:15.5',
            'openSUSE:Leap:15.6',
            'openSUSE:Leap:16.0',
            'openSUSE:Tumbleweed',
            'devel:languages:nodejs',
            'devel:languages:python',
            'devel:languages:python3',
            'server:Rancher',
            'Cloud:Tools',
            'Virtualization:containers',
        ]

    def get_project_packages(self, project: str) -> List[str]:
        """Get all packages in a project"""
        url = f'{self.obs_base}/source/{project}'

        try:
            resp = self.session.get(url)
            if resp.status_code != 200:
                print(f"  Error accessing {project}: {resp.status_code}")
                return []

            root = ET.fromstring(resp.content)
            packages = [entry.get('name') for entry in root.findall('entry') if entry.get('name')]
            return packages
        except Exception as e:
            print(f"  Error parsing {project}: {e}")
            return []

    def get_package_history(self, project: str, package: str) -> List[Dict]:
        """Get package commit history"""
        url = f'{self.obs_base}/source/{project}/{package}/_history'

        try:
            resp = self.session.get(url)
            if resp.status_code != 200:
                return []

            root = ET.fromstring(resp.content)
            history = []

            for revision in root.findall('revision'):
                rev_time = revision.find('time').text if revision.find('time') is not None else None
                if rev_time:
                    # Parse time: Unix timestamp
                    rev_datetime = datetime.fromtimestamp(int(rev_time))
                    history.append({
                        'rev': revision.get('rev'),
                        'datetime': rev_datetime,
                        'user': revision.find('user').text if revision.find('user') is not None else 'unknown'
                    })

            return history
        except:
            return []

    def was_updated_since_attack(self, project: str, package: str) -> bool:
        """Check if package was updated since attack date"""
        history = self.get_package_history(project, package)

        if not history:
            # No history available, skip
            return False

        # Check if any revision is after attack start date
        for rev in history:
            if rev['datetime'] >= self.attack_start_date:
                return True

        return False

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

    def get_package_files(self, project: str, package: str) -> List[str]:
        """Get files in a package"""
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

    def check_for_compromised_packages(self, content: str) -> List[Dict]:
        """Check content for compromised package references"""
        findings = []

        for attack in self.compromised:
            pkg_name = attack['package_name']

            # Check if package is mentioned
            if pkg_name in content or pkg_name.lower() in content.lower():
                # Check for specific malicious versions
                for mal_ver in attack['malicious_versions']:
                    if mal_ver in content:
                        findings.append({
                            'package': pkg_name,
                            'version': mal_ver,
                            'ecosystem': attack['ecosystem'],
                            'attack_type': attack['attack_type']
                        })

        return findings

    def scan_package(self, project: str, package: str) -> Dict:
        """Scan a package for compromised dependencies"""
        result = {
            'project': project,
            'package': package,
            'findings': [],
            'status': 'clean',
            'files_checked': []
        }

        files = self.get_package_files(project, package)

        # Files to check
        relevant_files = [f for f in files if (
            f.endswith('.spec') or
            f == 'package.json' or
            f == 'package-lock.json' or
            f == 'requirements.txt' or
            f == 'Pipfile' or
            f == 'Pipfile.lock' or
            f == 'pyproject.toml'
        )]

        for filename in relevant_files:
            content = self.get_file_content(project, package, filename)
            if content:
                result['files_checked'].append(filename)
                findings = self.check_for_compromised_packages(content)

                if findings:
                    for f in findings:
                        f['file'] = filename
                    result['findings'].extend(findings)

            time.sleep(0.1)

        if result['findings']:
            result['status'] = 'COMPROMISED'

        return result

    def scan_project(self, project: str, check_update_time: bool = True) -> List[Dict]:
        """Scan all relevant packages in a project"""
        print(f"\n{'='*70}")
        print(f"Scanning project: {project}")
        print(f"{'='*70}")

        packages = self.get_project_packages(project)
        if not packages:
            print(f"  No packages found or access denied")
            return []

        # Filter to packages that might contain npm/python dependencies
        keywords = ['node', 'npm', 'python', 'py', 'rancher', 'kubernetes',
                   'k8s', 'docker', 'container', 'helm', 'operator']

        relevant_packages = [p for p in packages if any(k in p.lower() for k in keywords)]

        print(f"  Total packages: {len(packages)}")
        print(f"  Relevant packages (node/python/container): {len(relevant_packages)}")

        if check_update_time:
            print(f"  Filtering to packages updated since {self.attack_start_date.strftime('%Y-%m-%d')}...")

            # Check update times (this is slow, so limit initial set)
            updated_packages = []
            for i, pkg in enumerate(relevant_packages[:100], 1):  # Limit to first 100 relevant
                if i % 20 == 0:
                    print(f"    Checked {i}/{min(len(relevant_packages), 100)} packages...")

                if self.was_updated_since_attack(project, pkg):
                    updated_packages.append(pkg)
                time.sleep(0.2)

            packages_to_scan = updated_packages
            print(f"  Packages updated since attack: {len(packages_to_scan)}")
        else:
            # Just scan first 50 relevant packages
            packages_to_scan = relevant_packages[:50]
            print(f"  Scanning first 50 relevant packages")

        if not packages_to_scan:
            print(f"  No packages to scan")
            return []

        results = []
        for i, package in enumerate(packages_to_scan, 1):
            print(f"  [{i}/{len(packages_to_scan)}] Scanning {package}...", end=' ')

            result = self.scan_package(project, package)
            results.append(result)

            if result['status'] == 'COMPROMISED':
                print(f"⚠️  COMPROMISED! ({len(result['findings'])} findings)")
            else:
                print(f"✓")

            time.sleep(0.3)

        return results

def main():
    print(f"Comprehensive OBS Scanner for Supply Chain Attacks")
    print(f"Started at: {datetime.now().isoformat()}")
    print(f"=" * 70)

    scanner = OBSComprehensiveScanner()

    print(f"\nAttack Discovery Date: {scanner.attack_start_date.strftime('%Y-%m-%d')}")
    print(f"Scanning SUSE-responsible projects for updates since that date")
    print(f"Projects to scan: {len(scanner.suse_projects)}")

    # Create output filename
    output_file = f'reports/obs_comprehensive_scan_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    all_results = {}

    for project in scanner.suse_projects:
        try:
            results = scanner.scan_project(project, check_update_time=True)
            all_results[project] = results

            # Save incremental progress
            with open(output_file, 'w') as f:
                json.dump(all_results, f, indent=2)
            print(f"Progress saved to {output_file}")

        except Exception as e:
            print(f"Error scanning {project}: {e}")
            all_results[project] = {'error': str(e)}

    # Final summary
    print(f"\n{'='*70}")
    print(f"SCAN COMPLETE")
    print(f"{'='*70}")

    total_packages = sum(len(v) if isinstance(v, list) else 0 for v in all_results.values())
    compromised = sum(1 for v in all_results.values() if isinstance(v, list)
                     for pkg in v if pkg.get('status') == 'COMPROMISED')

    print(f"Total packages scanned: {total_packages}")
    print(f"Compromised packages: {compromised}")
    print(f"Results saved to: {output_file}")
    print(f"Finished at: {datetime.now().isoformat()}")

if __name__ == '__main__':
    main()
