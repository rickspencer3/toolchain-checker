# @antv / Mini Shai-Hulud Wave 4 Supply Chain Attack

**Report Date:** May 19, 2026  
**Attack Discovered:** May 19, 2026 (01:56–02:56 UTC) — **TODAY**  
**Status:** ✅ **ALL CLEAR — SCAN COMPLETE**

---

## Executive Summary

A new wave of the Mini Shai-Hulud supply chain attack was detected today targeting the entire `@antv` data visualization ecosystem on npm. The attacker compromised the `atool` maintainer account (`antvis@aliyun.com`) and published **631 malicious versions across 314 packages** in a 22-minute automated burst.

**Risk to SUSE:** ✅ **NONE** — Full scan completed. Zero compromised packages found across 75 repositories.

---

## Attack Details

| Field | Value |
|-------|-------|
| **Ecosystem** | npm |
| **Attack Time** | May 19, 2026, 01:56–02:56 UTC |
| **Packages Affected** | 314+ packages, 631+ malicious versions |
| **Attribution** | TeamPCP / Mini Shai-Hulud |
| **Method** | Compromised npm maintainer account (`atool`) |
| **Payload** | 498KB obfuscated Bun script via `preinstall` hook |
| **C2 Server** | `t.m-kosche.com:443` |
| **Fallback Exfil** | GitHub dead-drop repos ("Shai-Hulud: Here We Go Again") |
| **Severity** | CRITICAL |

---

## Compromised Packages (Key Packages)

### High-Download Packages

| Package | Malicious Versions | Monthly Downloads |
|---------|-------------------|------------------|
| `size-sensor` | 1.1.4, 1.2.4 | 4.2M |
| `echarts-for-react` | 3.1.7, 3.2.7 | 3.8M |
| `@antv/scale` | (various) | 2.2M |
| `timeago.js` | 4.1.2, 4.2.2 | 1.15M |

### Core @antv Packages

| Package | Malicious Versions |
|---------|-------------------|
| `@antv/g2` | 5.5.8, 5.6.8 |
| `@antv/g6` | 5.2.1, 5.3.1 |
| `@antv/x6` | 3.2.7, 3.3.7 |
| `@antv/l7` | 2.26.10, 2.27.10 |
| `@antv/s2` | 2.8.1, 2.9.1 |
| `@antv/f2` | 5.15.0, 5.16.0 |
| `@antv/g` | 6.4.1, 6.5.1 |
| `@antv/g2plot` | 2.5.35, 2.6.35 |
| `@antv/graphin` | 3.1.5, 3.2.5 |
| `@antv/data-set` | 0.12.8, 0.13.8 |
| `@antv/util` | 3.4.11, 3.5.11 |
| `@antv/g-lite` | 2.8.0, 2.9.0 |
| `canvas-nest.js` | 2.1.4, 2.2.4 |

> **Pattern:** Each package received exactly two malicious versions — matching the TanStack wave pattern.
> **Full list:** 314 packages with 2 versions each (plus existing malicious versions from prior packages).

---

## Attack Mechanism

### How the Attack Spreads

1. **Initial access:** Stolen credentials for npm maintainer account `atool`
2. **Automated burst:** Scripts published 631 malicious versions in 22 minutes
3. **Payload delivery:** `preinstall` hook runs `bun run index.js` before npm install completes
4. **Worm propagation:** Payload scans for additional npm tokens → publishes to more packages
5. **Persistence:** Plants backdoors in `.claude/` and `.vscode/` directories

### semver Resolution Risk

The attacker did NOT move the `latest` dist-tag. However, this provides **no protection**:

```
"echarts-for-react": "^3.0.6"  →  resolves to 3.2.7 (MALICIOUS) on next clean install
```

Any project using `^` or `~` ranges may automatically pull malicious versions.

### What Gets Stolen

The payload targets **20+ credential types**:
- AWS IAM credentials, GCP service accounts, Azure secrets
- GitHub tokens and npm tokens
- SSH private keys
- Kubernetes service account tokens
- HashiCorp Vault secrets
- Stripe API keys
- Database connection strings
- Cryptocurrency wallet files
- **CI/CD runner memory** (reads masked secrets from GitHub Actions runner heap)
- **Docker container escape** via host socket

---

## SUSE Scan Results

### High-Priority Repositories to Check

The following SUSE/Rancher repositories are most likely to use @antv visualization packages:

| Repository | Risk Level | Reason |
|-----------|-----------|--------|
| `rancher/dashboard` | HIGH | Main Rancher UI — uses many npm packages |
| `rancher/ui` | MEDIUM | Legacy Rancher UI |
| `rancher/kubewarden-ui` | MEDIUM | TypeScript frontend |
| `rancher/security-ui-exts` | MEDIUM | TypeScript frontend |
| `openSUSE/cockpit*` | MEDIUM | Web-based server management UI |

### Scan Results

**GitHub Scan:** ✅ COMPLETE — May 19, 2026 (11:27–11:44 UTC, 17 minutes)

| Organization | Repos Scanned | Result |
|-------------|--------------|--------|
| SUSE | 16 | ✅ ALL CLEAN |
| rancher | 15 | ✅ ALL CLEAN |
| SUSE-Rancher-Community | 0 (no matches) | ✅ CLEAN |
| rancher-sandbox | 4 | ✅ ALL CLEAN |
| openSUSE | 40 | ✅ ALL CLEAN |
| **TOTAL** | **75** | **✅ ZERO COMPROMISED** |

High-priority repos checked:
- ✅ `rancher/dashboard` — CLEAN (no @antv packages)
- ✅ `rancher/ui` — CLEAN
- ✅ `rancher/kubewarden-ui` — CLEAN
- ✅ `rancher/security-ui-exts` — CLEAN
- ✅ `openSUSE/cockpit` — CLEAN
- ✅ `openSUSE/cockpit-tukit`, `cockpit-subscriptions`, `cockpit-repos`, `cockpit-packages`, `cockpit-snapshots`, `cockpit-bootloader` — ALL CLEAN

Full results: `reports/github_scan_20260519_112722.json`

**OBS Scan:** ✅ COMPLETE — 9 recently updated packages scanned, 0 compromised.

Full results: `reports/obs_recent_scan_20260519_114504.json`

---

## Threat Context: Mini Shai-Hulud Campaign Timeline

| Date | Event |
|------|-------|
| Apr 21, 2026 | pgserve, @automagik/genie (npm) compromised |
| Apr 22, 2026 | xinference (PyPI) compromised |
| Apr 23, 2026 | @bitwarden/cli (npm) compromised |
| Apr 30, 2026 | pytorch-lightning (PyPI) compromised |
| May 11, 2026 | TanStack (42 npm), @mistralai, @uipath, @squawk, @opensearch compromised |
| May 12, 2026 | mistralai, guardrails-ai (PyPI) compromised |
| May 14, 2026 | node-ipc (npm, 10M+ downloads/week) compromised |
| **May 19, 2026** | **@antv ecosystem (314+ npm packages) compromised — TODAY** |

**Total campaign scope:** 502+ unique packages, 1,055+ malicious versions across npm and PyPI.

---

## Immediate Recommendations

### For SUSE Developers

1. **Check package-lock.json** for any @antv, echarts-for-react, timeago.js, or size-sensor entries
2. **Do not run `npm install`** until clean versions are confirmed
3. **Rotate credentials** on any machine where these packages may have run
4. **Audit `.claude/` and `.vscode/`** for unexpected files:
   - Legitimate `.claude/` files: `settings.json`, `settings.local.json`, `keybindings.json`, `scheduled_tasks.json`
   - Any other JS files in these directories = potential persistence hook

### For CI/CD Systems

5. **Check runner logs** from May 19, 01:56–02:56 UTC for any npm install activity
6. **Rotate all CI secrets** if any jobs ran during the attack window
7. **Remove persistence daemon** if found:
   - Linux: `~/.config/systemd/user/gh-token-monitor.service`
   - macOS: `~/Library/LaunchAgents/com.user.gh-token-monitor.plist`

### Safe Versions

Use versions published **before May 19, 2026, 01:56 UTC** or **after cleanup** (monitor npm advisories for when clean versions are republished).

---

## Sources

- [Mini Shai-Hulud Pushes Malicious AntV npm Packages - The Hacker News](https://thehackernews.com/2026/05/mini-shai-hulud-pushes-malicious-antv.html)
- [Active Supply Chain Attack Compromises @antv Packages on npm - Socket](https://socket.dev/blog/antv-packages-compromised)
- [Mini Shai-Hulud Strikes Again: 314 npm Packages Compromised - SafeDep](https://safedep.io/mini-shai-hulud-strikes-again-314-npm-packages-compromised/)
- [The @antv Ecosystem Was Compromised with Shai-Hulud Malware - OX Security](https://www.ox.security/blog/the-antv-ecosystem-was-compromised-with-shai-hulud-malware-300-packages-affected)
- [Mini Shai-Hulud Attack Hits @antv npm Packages - GBHackers](https://gbhackers.com/mini-shai-hulud-attack/)

---

**Report Generated:** May 19, 2026  
**Scan Tool:** toolchain-checker v2.0  
**Full Scan Results:** reports/github_scan_20260519_*.json (pending)
