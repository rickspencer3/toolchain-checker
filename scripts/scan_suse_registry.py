#!/usr/bin/env python3
"""
SUSE Container Registry Scanner for Supply Chain Attacks
Scans container images at registry.suse.com for compromised packages

NOTE: This scanner requires:
1. Docker or Podman installed
2. Authentication credentials for registry.suse.com (if required)
3. Sufficient disk space to pull container images

The registry uses Docker Registry API v2:
- Base URL: https://registry.suse.com
- API endpoint: https://registry.suse.com/v2/
- Authentication: Required for most operations
"""

import json
import requests
import subprocess
import tempfile
import os
from typing import Dict, List, Set
from datetime import datetime

class SUSERegistryScanner:
    def __init__(self, registry_url='registry.suse.com'):
        self.registry_url = registry_url
        self.api_base = f'https://{registry_url}/v2'
        self.session = requests.Session()

        # Load compromised packages
        with open('scripts/compromised_packages.json', 'r') as f:
            data = json.load(f)
            self.compromised = data['attacks']

        # Known SUSE container repositories (from web catalog)
        # This list should be updated by scanning the web interface or using API
        self.known_repos = [
            'bci-python314',
            'bci-python313',
            'bci-python311',
            'bci-openjdk25-devel',
            'bci-openjdk25',
            'bci-openjdk-devel21',
            'bci-openjdk21',
            'rmt',
            'suse-agentic-mcp-multi-linux-manager',
            # Add more as discovered
        ]

        self.results = {
            'scan_timestamp': datetime.now().isoformat(),
            'registry': registry_url,
            'images_scanned': [],
            'images_affected': [],
            'total_images_checked': 0,
            'total_affected': 0
        }

    def check_docker_available(self) -> bool:
        """Check if Docker or Podman is available"""
        for cmd in ['docker', 'podman']:
            try:
                result = subprocess.run([cmd, '--version'],
                                      capture_output=True,
                                      timeout=5)
                if result.returncode == 0:
                    print(f"✓ Found {cmd}")
                    self.container_cmd = cmd
                    return True
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue

        print("✗ Neither Docker nor Podman found")
        print("  Install with: zypper install docker or zypper install podman")
        return False

    def authenticate_registry(self, username=None, password=None):
        """
        Authenticate with registry.suse.com

        Options:
        1. Use SUSE customer credentials
        2. Check if anonymous access is available for some repos
        3. Use service account credentials
        """
        if username and password:
            # Login using container runtime
            result = subprocess.run(
                [self.container_cmd, 'login', self.registry_url,
                 '-u', username, '-p', password],
                capture_output=True
            )
            return result.returncode == 0

        # Try anonymous access
        try:
            resp = self.session.get(f'{self.api_base}/')
            if resp.status_code == 200:
                print("✓ Anonymous access available")
                return True
        except:
            pass

        print("⚠ Authentication required")
        print("  Set REGISTRY_USERNAME and REGISTRY_PASSWORD environment variables")
        return False

    def list_repositories(self) -> List[str]:
        """
        List all repositories in the registry

        This requires authentication and uses Docker Registry API v2
        GET /v2/_catalog
        """
        try:
            resp = self.session.get(f'{self.api_base}/_catalog')
            if resp.status_code == 200:
                data = resp.json()
                return data.get('repositories', [])
            elif resp.status_code == 401:
                print("⚠ Authentication required to list repositories")
                return self.known_repos  # Fall back to known list
        except Exception as e:
            print(f"✗ Error listing repositories: {e}")
            return self.known_repos

    def get_image_tags(self, repo: str) -> List[str]:
        """Get all tags for a repository"""
        try:
            resp = self.session.get(f'{self.api_base}/{repo}/tags/list')
            if resp.status_code == 200:
                data = resp.json()
                return data.get('tags', [])
        except Exception as e:
            print(f"✗ Error getting tags for {repo}: {e}")
        return []

    def scan_container_image(self, image_name: str, tag: str = 'latest') -> Dict:
        """
        Scan a container image for compromised packages

        Process:
        1. Pull the image
        2. Create a temporary container
        3. Extract dependency files (requirements.txt, package.json, etc.)
        4. Check against compromised packages list
        5. Clean up
        """
        full_image = f'{self.registry_url}/{image_name}:{tag}'

        print(f"\n{'='*60}")
        print(f"Scanning: {full_image}")
        print(f"{'='*60}")

        result = {
            'image': full_image,
            'affected': False,
            'findings': []
        }

        try:
            # Pull the image
            print(f"  Pulling image...")
            pull_result = subprocess.run(
                [self.container_cmd, 'pull', full_image],
                capture_output=True,
                timeout=300  # 5 minute timeout
            )

            if pull_result.returncode != 0:
                print(f"  ✗ Failed to pull image")
                result['error'] = 'Failed to pull image'
                return result

            print(f"  ✓ Image pulled successfully")

            # Create temporary container to inspect filesystem
            with tempfile.TemporaryDirectory() as tmpdir:
                # Extract dependency files from container
                dependency_files = [
                    '/requirements.txt',
                    '/app/requirements.txt',
                    '/usr/src/app/requirements.txt',
                    '/package.json',
                    '/app/package.json',
                    '/usr/src/app/package.json',
                ]

                for dep_file in dependency_files:
                    # Try to copy file from container
                    # Note: This creates a temporary container
                    copy_result = subprocess.run(
                        [self.container_cmd, 'run', '--rm',
                         '-v', f'{tmpdir}:/output',
                         full_image,
                         'sh', '-c',
                         f'if [ -f {dep_file} ]; then cp {dep_file} /output/; fi'],
                        capture_output=True,
                        timeout=30
                    )

                    # Check if file was extracted
                    local_file = os.path.join(tmpdir, os.path.basename(dep_file))
                    if os.path.exists(local_file):
                        print(f"  ✓ Found {dep_file}")

                        # Scan the file
                        with open(local_file, 'r') as f:
                            content = f.read()
                            findings = self.check_dependencies(content, dep_file)
                            if findings:
                                result['affected'] = True
                                result['findings'].extend(findings)

            if result['affected']:
                print(f"  🚨 AFFECTED: {len(result['findings'])} compromised packages found")
            else:
                print(f"  ✓ CLEAN: No compromised packages found")

        except subprocess.TimeoutExpired:
            print(f"  ✗ Timeout while scanning image")
            result['error'] = 'Timeout'
        except Exception as e:
            print(f"  ✗ Error: {e}")
            result['error'] = str(e)

        return result

    def check_dependencies(self, content: str, filename: str) -> List[str]:
        """Check dependency file content against compromised packages"""
        findings = []

        for attack in self.compromised:
            package_name = attack['package_name']
            malicious_versions = attack['malicious_versions']

            # Simple text search (should be enhanced with proper parsing)
            if package_name in content.lower():
                for version in malicious_versions:
                    if version in content:
                        findings.append(
                            f"{filename}: {package_name}=={version} (MALICIOUS)"
                        )

        return findings

    def scan_all(self):
        """Scan all container images in the registry"""
        print(f"\n{'*'*60}")
        print(f"SUSE Container Registry Scanner")
        print(f"Registry: {self.registry_url}")
        print(f"{'*'*60}")

        # Check Docker/Podman availability
        if not self.check_docker_available():
            print("\n⚠ Cannot scan without Docker or Podman")
            print("Install instructions:")
            print("  SLES: zypper install docker")
            print("  Ubuntu: apt-get install docker.io")
            print("  Fedora: dnf install podman")
            return

        # Authenticate
        username = os.environ.get('REGISTRY_USERNAME')
        password = os.environ.get('REGISTRY_PASSWORD')

        if not self.authenticate_registry(username, password):
            print("\n⚠ Proceeding with known repository list")
            print("  For full scan, provide credentials via environment variables:")
            print("  export REGISTRY_USERNAME='your-username'")
            print("  export REGISTRY_PASSWORD='your-password'")

        # List repositories
        repos = self.list_repositories()
        print(f"\n✓ Found {len(repos)} repositories to scan")

        # Scan each repository
        for repo in repos:
            # Get tags (or use 'latest')
            tags = self.get_image_tags(repo)
            if not tags:
                tags = ['latest']

            # Scan latest tag only (to save time)
            # For comprehensive scan, iterate through all tags
            result = self.scan_container_image(repo, tags[0] if tags else 'latest')

            self.results['images_scanned'].append(result['image'])
            if result.get('affected'):
                self.results['images_affected'].append(result)
                self.results['total_affected'] += 1

            self.results['total_images_checked'] += 1

            # Save incremental results
            self.save_results()

        self.print_summary()

    def save_results(self):
        """Save scan results to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'reports/registry_scan_{timestamp}.json'

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n[Results saved to {output_file}]")

    def print_summary(self):
        """Print scan summary"""
        print(f"\n\n{'='*60}")
        print(f"SCAN SUMMARY")
        print(f"{'='*60}")
        print(f"Registry: {self.registry_url}")
        print(f"Total images checked: {self.results['total_images_checked']}")
        print(f"Affected images: {self.results['total_affected']}")

        if self.results['images_affected']:
            print(f"\n🚨 AFFECTED IMAGES:")
            for result in self.results['images_affected']:
                print(f"  - {result['image']}")
                for finding in result['findings']:
                    print(f"      {finding}")
        else:
            print(f"\n✅ ALL CLEAR: No compromised packages found in container images")

        print(f"{'='*60}\n")


def main():
    """
    Main entry point for SUSE Registry scanner

    Usage:
        # Basic scan
        python3 scripts/scan_suse_registry.py

        # With authentication
        export REGISTRY_USERNAME='your-username'
        export REGISTRY_PASSWORD='your-password'
        python3 scripts/scan_suse_registry.py
    """
    scanner = SUSERegistryScanner()
    scanner.scan_all()


if __name__ == '__main__':
    main()
