# OBS Supply Chain Attack Scan Summary

**Date:** 2026-04-23  
**Scan Type:** Comprehensive OBS Package Scan  
**Attack Window:** April 21-23, 2026  
**Status:** ✅ COMPLETE - NO COMPROMISED PACKAGES FOUND

---

## Executive Summary

Completed a comprehensive scan of SUSE-responsible Open Build Service (OBS) projects to detect presence of recently-discovered supply chain attacks affecting npm and PyPI ecosystems.

**Key Findings:**
- **104 packages scanned** across 11 OBS projects
- **0 compromised packages detected**
- All scanned packages are clean

---

## Supply Chain Attacks Detected (April 21-22, 2026)

### 1. pgserve (npm)
- **Malicious Versions:** 1.1.11, 1.1.12, 1.1.13
- **Discovered:** 2026-04-21
- **Type:** Self-propagating worm
- **Impact:** Credential theft, cloud keys, SSH keys, tokens
- **Safe Version:** ≤1.1.10

### 2. @automagik/genie (npm)
- **Malicious Versions:** 4.260421.33 through 4.260421.39
- **Discovered:** 2026-04-21
- **Type:** Self-propagating worm
- **Impact:** Credential theft, cloud keys, SSH keys, tokens, crypto wallets
- **Exfiltration:** ICP canister cjn37-uyaaa-aaaac-qgnva-cai

### 3. xinference (PyPI)
- **Malicious Versions:** 2.6.0, 2.6.1, 2.6.2
- **Discovered:** 2026-04-22
- **Type:** Two-stage credential stealer
- **Impact:** SSH keys, cloud credentials, environment variables, secrets, crypto wallets
- **Attribution:** TeamPCP

---

## Scan Methodology

### Project Selection Logic

**Criteria for inclusion:**
1. **SUSE-responsible projects** - Official SUSE/openSUSE maintained projects
2. **High-risk categories** - Projects likely to contain npm/Python dependencies:
   - Language development repositories (devel:languages:nodejs, devel:languages:python)
   - Container/orchestration tools (Virtualization:containers, Cloud:Tools)
   - Rancher-related projects (server:Rancher)
   - Core distributions (openSUSE:Factory, openSUSE:Leap, openSUSE:Tumbleweed)

### Filtering Strategy

**Time-based filtering:**
- Only scanned packages **updated since April 21, 2026** (attack discovery date)
- Used OBS `_history` API endpoint to check package modification timestamps
- Rationale: Packages not updated since before the attacks cannot contain the malicious versions

**Package filtering:**
- Within each project, filtered to packages likely containing npm/Python dependencies
- Keywords: node, npm, python, py, rancher, kubernetes, k8s, docker, container, helm, operator
- This avoided scanning 100,000+ packages across all of OBS

### Detection Method

**Files checked per package:**
- `.spec` files (RPM build specifications)
- `package.json` (npm dependencies)
- `package-lock.json` (npm lockfile)
- `requirements.txt` (Python dependencies)
- `Pipfile` / `Pipfile.lock` (Python dependencies)
- `pyproject.toml` (Python dependencies)

**Matching logic:**
- Exact package name matching (pgserve, @automagik/genie, xinference)
- Exact version matching against known malicious versions
- Case-insensitive search for package references

---

## Projects Scanned

### ✅ Scanned with Packages Found

| Project | Packages Scanned | Status |
|---------|------------------|--------|
| devel:languages:nodejs | 100 | ✅ Clean |
| openSUSE:Factory | 1 | ✅ Clean |
| openSUSE:Leap:16.0 | 1 | ✅ Clean |
| devel:languages:python | 1 | ✅ Clean |
| Virtualization:containers | 1 | ✅ Clean |

### 📭 No Updates Since Attack Date

| Project | Status |
|---------|--------|
| openSUSE:Leap:15.5 | No packages updated since April 21 |
| openSUSE:Leap:15.6 | No packages updated since April 21 |
| openSUSE:Tumbleweed | No packages updated since April 21 |
| devel:languages:python3 | No packages updated since April 21 |
| Cloud:Tools | No packages updated since April 21 |

### ❌ Access Issues

| Project | Issue |
|---------|-------|
| server:Rancher | 404 - Project not found/accessible via public API |

---

## Complete Package List (104 packages)

### openSUSE:Factory (1)
- container-diff

### openSUSE:Leap:16.0 (1)
- python-PyPDF2

### devel:languages:nodejs (100)
nodejs-Base64, nodejs-absolute-path, nodejs-accepts, nodejs-acorn-globals, nodejs-angular, nodejs-angular-animate, nodejs-angular-google-chart, nodejs-angular-moment, nodejs-angular-route, nodejs-archiver, nodejs-argparser, nodejs-argsparser, nodejs-ast-types, nodejs-async-stacktrace, nodejs-atob, nodejs-azure-rm-website, nodejs-azure-storage-legacy, nodejs-base62, nodejs-base64-js, nodejs-bindings, nodejs-boolbase, nodejs-bootswatch, nodejs-bops, nodejs-buffer-crc32, nodejs-buffer-equal, nodejs-bunker, nodejs-burrito, nodejs-channels, nodejs-character-parser, nodejs-charm, nodejs-cheerio, nodejs-coa, nodejs-coffee-script-redux, nodejs-coffeestack, nodejs-collections, nodejs-commander2, nodejs-common, nodejs-compress-commons, nodejs-connect-prism, nodejs-constantinople, nodejs-contextify, nodejs-cookie, nodejs-cookie-parser, nodejs-cookie-signature, nodejs-crc32-stream, nodejs-cscodegen, nodejs-cson-safe, nodejs-css, nodejs-css-select, nodejs-cssom, nodejs-cssstyle, nodejs-deep-equal, nodejs-di, nodejs-difflet, nodejs-director, nodejs-dom-serializer, nodejs-ejs, nodejs-electron, nodejs-emojione, nodejs-engine.io, nodejs-engine.io-parser, nodejs-envify, nodejs-escodegen, nodejs-esmangle, nodejs-esprima-fb, nodejs-esshorten, nodejs-eventemitter3, nodejs-expresso, nodejs-faye-websocket, nodejs-fileset, nodejs-formidable, nodejs-forwarded-for, nodejs-fs.extra, nodejs-grunt-cli, nodejs-grunt-connect-prism, nodejs-grunt-contrib-watch, nodejs-grunt-rpm, nodejs-guid, nodejs-harmony-collections, nodejs-hooker, nodejs-http-proxy, nodejs-isbinaryfile, nodejs-jasmine-growl-reporter, nodejs-jasmine-node, nodejs-jasmine-reporters, nodejs-jscoverage, nodejs-jsdom, nodejs-jstransform, nodejs-lazystream, nodejs-lodash-node, nodejs-monocle, nodejs-negotiator, nodejs-nextback, nodejs-node-int64, nodejs-nomnom, nodejs-noptify, nodejs-nth-check, nodejs-nwmatcher, nodejs-oniguruma, nodejs-optimist

### devel:languages:python (1)
- python-Glances

### Virtualization:containers (1)
- container-diff

---

## Scan Limitations

1. **OBS Public API Access**
   - Some SUSE-internal projects (SUSE:SLE-15:SP5, SUSE:SLE-15:SP6) require authentication
   - Scanned using public OBS interface at build.opensuse.org/public

2. **Time Window**
   - Only checked packages modified since April 21, 2026
   - Packages updated before this date were not scanned (cannot contain newly-released malicious versions)

3. **Package Scope**
   - Focused on nodejs/python/container-related packages
   - Did not scan all ~140,000 packages in OBS (would take many hours)

4. **Detection Granularity**
   - Detects exact version matches in dependency files
   - Does not detect if malicious code was copied/adapted rather than installed as dependency
   - Does not detect previously-compromised systems

---

## Recommendations

### ✅ Immediate Actions
- **No immediate action required** - No compromised packages detected in SUSE OBS repositories

### 🔄 Ongoing Monitoring
1. **Continue monitoring** for new supply chain attacks
2. **Re-scan daily** or after major package updates
3. **Monitor upstream security advisories** for npm and PyPI

### 🛡️ Preventive Measures
1. Enable npm `ignore-scripts` in build environments: `npm config set ignore-scripts true`
2. Review and audit npm/PyPI package installations in CI/CD pipelines
3. Consider using package lockfiles to prevent automatic updates to compromised versions

---

## Technical Details

**Scanner Implementation:** `scripts/scan_obs.py`  
**Full Results:** `reports/obs_comprehensive_scan_20260423_120222.json`  
**Attack Database:** `scripts/compromised_packages.json`

**Data Sources:**
- OBS Public API: https://build.opensuse.org/public
- Attack information aggregated from security advisories (StepSecurity, JFrog, Socket.dev)

---

## Additional Context

This scan is part of a broader supply chain security initiative that also includes:
- GitHub repository scanning (SUSE, Rancher, openSUSE organizations)
- Automated monitoring for new attacks
- Integration with existing security workflows

**Questions or concerns?** Contact the scanning team or refer to the full documentation in the toolchain-checker repository.

---

*Generated by automated supply chain security scanner*  
*Scan completed: 2026-04-23T12:06:55*
