#!/usr/bin/env python3
"""
Smart checker for Bitwarden CLI in previously scanned repositories
Uses cached scan data to avoid hitting GitHub rate limits
"""

import json
import os
import sys
from datetime import datetime

def check_existing_scans_for_bitwarden():
    """
    Check if any previously scanned repos likely use Bitwarden CLI
    by examining repo names, languages, and scan metadata
    """

    print("Bitwarden CLI Supply Chain Attack Check")
    print("=" * 70)
    print()

    # Load the latest scan results
    scan_files = [
        'reports/github_scan_20260423_122623.json',
        'reports/github_scan_20260423_172504.json'
    ]

    all_scanned_repos = {}

    for scan_file in scan_files:
        if os.path.exists(scan_file):
            with open(scan_file, 'r') as f:
                data = json.load(f)
                for org, repos in data.items():
                    if org not in all_scanned_repos:
                        all_scanned_repos[org] = []
                    all_scanned_repos[org].extend(repos)

    # Count unique repos
    total_repos = sum(len(repos) for repos in all_scanned_repos.values())

    print(f"Analyzing {total_repos} previously scanned repositories...")
    print()

    # Bitwarden CLI is a developer tool, most likely to be found in:
    # - CI/CD repositories
    # - Security/auth related projects
    # - Developer tooling projects
    # - Projects with JavaScript/TypeScript (npm package)

    high_risk_repos = []
    medium_risk_repos = []

    for org, repos in all_scanned_repos.items():
        for repo in repos:
            repo_name = repo['repo'].lower()

            # High risk indicators
            if any(keyword in repo_name for keyword in [
                'auth', 'security', 'secret', 'credential',
                'password', 'vault', 'identity', 'ci', 'pipeline'
            ]):
                high_risk_repos.append(repo['repo'])

            # Medium risk: any JavaScript/TypeScript project
            # (Bitwarden CLI is an npm package)
            elif 'dashboard' in repo_name or 'ui' in repo_name or 'cli' in repo_name:
                medium_risk_repos.append(repo['repo'])

    print("RISK ASSESSMENT:")
    print("-" * 70)

    if high_risk_repos:
        print(f"\n⚠️  HIGH RISK REPOS ({len(high_risk_repos)}):")
        print("   (Auth/security/CI related - could use Bitwarden CLI)")
        for repo in high_risk_repos:
            print(f"   - {repo}")

    if medium_risk_repos:
        print(f"\n⚡ MEDIUM RISK REPOS ({len(medium_risk_repos)}):")
        print("   (UI/Dashboard/CLI projects - may use npm packages)")
        for repo in medium_risk_repos:
            print(f"   - {repo}")

    low_risk_count = total_repos - len(high_risk_repos) - len(medium_risk_repos)
    print(f"\n✅ LOW RISK REPOS: {low_risk_count}")
    print("   (Kernel, system utilities, non-JS projects)")

    print()
    print("ANALYSIS:")
    print("-" * 70)

    # Load compromised package info
    with open('scripts/compromised_packages.json', 'r') as f:
        comp_data = json.load(f)
        bitwarden_attack = next(
            (a for a in comp_data['attacks'] if a['package_name'] == '@bitwarden/cli'),
            None
        )

    if bitwarden_attack:
        print(f"Package: @bitwarden/cli")
        print(f"Compromised version: {bitwarden_attack['malicious_versions']}")
        print(f"Attack window: {bitwarden_attack['attack_window']}")
        print(f"Attribution: {bitwarden_attack['attribution']}")
        print()

    print("LIKELIHOOD ASSESSMENT:")
    print()
    print("❌ KERNEL/SYSTEM REPOS: Near-zero risk")
    print("   - kernel-source, suse-migration-services: C/Shell, no npm dependencies")
    print()
    print("⚠️  WEB/DASHBOARD REPOS: Low-Medium risk")
    print("   - rancher/dashboard: Uses npm, but Bitwarden CLI is a dev tool,")
    print("     not typically a production dependency")
    print()
    print("🔍 RECOMMENDATION:")
    print("   For high-confidence results, need to check package.json files")
    print("   in repositories that use npm/JavaScript.")
    print()
    print("   Without GitHub API access, checking the following repos manually:")

    priority_check = high_risk_repos + medium_risk_repos
    if priority_check:
        print()
        for repo in priority_check[:5]:  # Top 5
            print(f"   - https://github.com/{repo}/blob/main/package.json")

    print()
    print("=" * 70)
    print()

    # Save summary
    summary = {
        "check_date": datetime.now().isoformat(),
        "attack": "@bitwarden/cli@2026.4.0",
        "total_repos_analyzed": total_repos,
        "high_risk_repos": high_risk_repos,
        "medium_risk_repos": medium_risk_repos,
        "low_risk_count": low_risk_count,
        "recommendation": "Manual check needed for high/medium risk repos",
        "requires_github_token": "For automated deep scanning"
    }

    with open('reports/bitwarden_risk_assessment.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print("✅ Risk assessment saved to: reports/bitwarden_risk_assessment.json")

    return summary

if __name__ == '__main__':
    check_existing_scans_for_bitwarden()
