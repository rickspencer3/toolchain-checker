# TanStack/Mini Shai-Hulud Supply Chain Attack Report
**Report Date:** May 12, 2026  
**Attack Discovery:** May 11, 2026 (19:14-19:26 UTC)  
**Attack ID:** CVE-2026-45321  
**Severity:** CRITICAL (CVSS 9.6/10.0)  
**Attribution:** TeamPCP / Mini Shai-Hulud worm

---

## Executive Summary

On May 11, 2026, a sophisticated supply chain attack compromised **169 npm packages with 373 malicious versions** across the npm ecosystem. The attack, attributed to the TeamPCP threat group's "Mini Shai-Hulud" worm, represents a significant escalation in supply chain threats:

- **First npm worm with valid SLSA Build Level 3 provenance** (packages appear fully legitimate)
- **Self-propagating malware** that used stolen credentials to spread across the ecosystem
- **Critical infrastructure targeted** including AI frameworks (Mistral AI), automation platforms (UiPath), and popular frontend tools (TanStack Router)

---

## Attack Overview

### Attack Vector
The attacker exploited a sophisticated chain of vulnerabilities:

1. **GitHub Actions `pull_request_target` exploit** (Pwn Request pattern)
2. **Cache poisoning across fork↔base trust boundary**
3. **OIDC token extraction from GitHub Actions runner memory**
4. **Self-propagation using stolen maintainer credentials**

### Timeline
- **April 16, 2026 21:34 CEST** - Vulnerability detected by Depi (25 days before exploitation)
- **May 11, 2026 19:20-19:26 UTC** - 84 malicious @tanstack packages published (6-minute window)
- **May 11-12, 2026** - Worm spread to 160+ additional packages
- **Within 20 minutes** - Detected by external security researcher
- **May 11, 2026** - All malicious versions deprecated by npm

### Malware Capabilities
The malicious packages exfiltrate:
- ☁️ Cloud credentials (AWS, Azure, GCP)
- 🔑 GitHub tokens and npm credentials
- 🔐 SSH private keys
- 💰 Cryptocurrency wallet seeds and private keys
- 📋 Environment variables and secrets
- 📝 Shell history files

---

## Affected Packages

### Primary Target: @tanstack/* (42 packages, 84 versions)

**Router & Core Packages:**
- `@tanstack/router-core`: 1.169.5, 1.169.8
- `@tanstack/react-router`: 1.169.5, 1.169.8
- `@tanstack/vue-router`: 1.169.5, 1.169.8
- `@tanstack/solid-router`: 1.169.5, 1.169.8
- `@tanstack/history`: 1.161.9, 1.161.12

**Development & Build Tools:**
- `@tanstack/router-plugin`: 1.167.38, 1.167.41
- `@tanstack/router-vite-plugin`: 1.166.53, 1.166.56
- `@tanstack/router-cli`: 1.166.46, 1.166.49
- `@tanstack/router-generator`: 1.166.45, 1.166.48
- `@tanstack/eslint-plugin-router`: 1.161.9, 1.161.12

**Start Framework:**
- `@tanstack/react-start`: 1.167.68, 1.167.71
- `@tanstack/solid-start`: 1.167.65, 1.167.68
- `@tanstack/vue-start`: 1.167.61, 1.167.64

**DevTools:**
- `@tanstack/router-devtools`: 1.166.16, 1.166.19
- `@tanstack/react-router-devtools`: 1.166.16, 1.166.19

**Server & Client Packages:**
- `@tanstack/react-start-server`: 1.166.55, 1.166.58
- `@tanstack/react-start-client`: 1.166.51, 1.166.54
- `@tanstack/start-server-core`: 1.167.33, 1.167.36
- `@tanstack/start-client-core`: 1.168.5, 1.168.8

**Adapters:**
- `@tanstack/zod-adapter`: 1.166.12, 1.166.15
- `@tanstack/valibot-adapter`: 1.166.12, 1.166.15
- `@tanstack/arktype-adapter`: 1.166.12, 1.166.15

**✅ CONFIRMED CLEAN @tanstack packages:**
- `@tanstack/query*` (all versions)
- `@tanstack/table*` (all versions)
- `@tanstack/form*` (all versions)
- `@tanstack/virtual*` (all versions)
- `@tanstack/store` (all versions)
- `@tanstack/start` (meta-package only)

### Secondary Targets (Worm Propagation)

**@mistralai/* (3 packages, 9 versions)**
- `@mistralai/mistralai`: 2.2.2, 2.2.3, 2.2.4
- `@mistralai/mistralai-gcp`: 1.7.1, 1.7.2, 1.7.3
- `@mistralai/mistralai-azure`: 1.7.1, 1.7.2, 1.7.3

**@uipath/* (66 packages)**
Key packages include:
- `@uipath/cli`: 1.0.1
- `@uipath/rpa-tool`: 0.9.5
- `@uipath/agent.sdk`: 0.0.18
- `@uipath/docsai-tool`: 1.0.1
- `@uipath/apollo-react`: 4.24.5
- `@uipath/apollo-core`: 5.9.2
- Plus 60+ additional UiPath packages

**@squawk/* (22+ packages, 87+ versions)**
Aviation/flight planning packages:
- `@squawk/mcp`: 0.9.1, 0.9.2, 0.9.3, 0.9.4
- `@squawk/types`: 0.8.2, 0.8.3, 0.8.4
- `@squawk/weather`: 0.5.6, 0.5.7, 0.5.8, 0.5.9
- `@squawk/airspace`: 0.8.1, 0.8.2, 0.8.3, 0.8.4
- `@squawk/airports`, `@squawk/navaids`, `@squawk/airways`, etc.

**@tallyui/* (10 packages)**
E-commerce connector packages:
- `@tallyui/core`: 0.2.1, 0.2.2, 0.2.3
- `@tallyui/connector-shopify`: 1.0.1, 1.0.2, 1.0.3
- `@tallyui/connector-woocommerce`: 1.0.1, 1.0.2, 1.0.3

**Other Compromised Scopes:**
- `@draftlab/*` (3 packages)
- `@draftauth/*` (2 packages)
- `@beproduct/*` (1 package, 18 versions)
- `@ml-toolkit-ts/*` (2 packages)
- `@mesadev/*` (3 packages)
- `@dirigible-ai/*` (1 package)
- `@supersurkhet/*` (2 packages)
- `@taskflow-corp/*` (1 package)
- `@tolka/*` (1 package)

**Unscoped Packages (39+ versions):**
- `safe-action`, `ts-dna`, `cross-stitch`, `cmux-agent-mcp`, `agentwork-cli`, `git-branch-selector`, `wot-api`, `git-git-git`, `nextmove-mcp`, `ml-toolkit-ts`

---

## SUSE Risk Assessment

### Risk Level: **LOW TO MODERATE**

### Analysis

**Low Risk Factors:**
1. **Technology Stack Mismatch**
   - TanStack Router is a **frontend routing library** for React/Vue/Solid apps
   - SUSE primarily develops **backend systems, infrastructure, and container platforms**
   - Most SUSE products use Go, Python, C/C++, Rust — not heavy npm dependencies

2. **Package Type**
   - Compromised packages are primarily **dev tools and frontend frameworks**
   - SUSE's focus is on **enterprise Linux, Kubernetes, system management**

3. **Container-First Approach**
   - SUSE's modern applications use **containerized deployments**
   - Container images (BCI, AI containers) are built from Dockerfiles in GitHub
   - Our scanners check source Dockerfiles, not runtime containers

**Moderate Risk Factors:**
1. **Web UI Components**
   - Some SUSE products have web-based dashboards (Rancher, Uyuni, Longhorn)
   - These may use modern JavaScript frameworks
   - **@tanstack/router** could potentially be used in these UIs

2. **AI Product Line**
   - **@mistralai/mistralai** is a high-risk package
   - SUSE AI products may integrate with Mistral AI models
   - Packages: `suse-ai-stack`, `suse-ai-up`, `suse-ai-observability`

3. **Developer Tooling**
   - CI/CD pipelines may use compromised packages as dev dependencies
   - GitHub Actions workflows could pull malicious packages during builds

4. **Rancher Ecosystem**
   - Rancher has extensive JavaScript/TypeScript components
   - Rancher UI uses modern frontend frameworks
   - **598 Rancher repositories** to check

### Recommended Actions

**IMMEDIATE (Priority 1):**
1. ✅ **Update compromised package database** (DONE)
2. 🔍 **Scan Rancher UI repositories** (high-priority due to modern JS stack)
3. 🔍 **Scan SUSE AI repositories** for @mistralai packages
4. 🔍 **Check GitHub Actions workflows** across all SUSE orgs

**SHORT-TERM (Priority 2):**
1. 🔍 **Comprehensive GitHub scan** of all SUSE, Rancher, openSUSE repos
2. 🔍 **OBS package scan** (check devel:languages:nodejs project)
3. 📋 **Manual verification** of web UI components (Rancher, Uyuni, Longhorn dashboards)
4. 🔐 **Audit CI/CD secrets** as precautionary measure

**LONG-TERM (Priority 3):**
1. 📝 **Implement automated scanning** for future supply chain attacks
2. 🔒 **Strengthen GitHub Actions security** (review pull_request_target usage)
3. 📊 **Monitor for SLSA provenance** (this attack shows provenance can be legitimately malicious)

---

## Scanning Status

### GitHub Scan: ⏸️ PENDING
**Status:** Waiting for GitHub token  
**Reason:** Code search API requires authentication  
**Rate Limit:** 60 requests/hour without token, 5000 requests/hour with token  
**Estimated Time:** 
- Without token: 6-8 hours (not recommended)
- With token: 10-15 minutes

**To enable fast scanning:**
```bash
# Create GitHub Personal Access Token with public_repo scope
# Save to .github_token file
echo "ghp_YOUR_TOKEN_HERE" > .github_token
python3 scripts/scan_github.py
```

### OBS Scan: ⏸️ PENDING
**Status:** Ready to run  
**Target:** `devel:languages:nodejs` (highest risk for npm packages)  
**Estimated Time:** 5-10 minutes

**To run:**
```bash
python3 scripts/scan_obs.py
```

### Alternative: Manual High-Priority Check

Without automated scans, recommend manual verification of:

**Rancher UI Projects:**
- `rancher/dashboard` - Main Rancher UI
- `rancher/ui` - Legacy Rancher UI
- `rancher/ui-driver-skel` - UI driver framework

**SUSE AI Projects:**
- `SUSE/suse-ai-stack`
- `SUSE/suse-ai-up`
- `SUSE/suse-ai-observability-extension`

**Uyuni/SUSE Manager:**
- `uyuni-project/uyuni` - May have web UI components

**Commands to check manually:**
```bash
# Check for @tanstack in package.json
gh repo view rancher/dashboard -- cat package.json | grep tanstack

# Check for @mistralai
gh repo view SUSE/suse-ai-stack -- cat package.json | grep mistralai
```

---

## Technical Details

### Attack Mechanism

1. **Initial Compromise:**
   - Attacker submitted malicious PR to TanStack Router repository
   - Exploited `pull_request_target` workflow with unsafe fork code checkout
   - Clobbered Git post-checkout hook to poison pnpm cache

2. **Privilege Escalation:**
   - Contaminated TanStack's release workflow (had npm write permissions)
   - Extracted OIDC token from GitHub Actions runner memory
   - Published 84 malicious versions using TanStack's legitimate CI pipeline

3. **Worm Propagation:**
   - Malware enumerated all packages where victim has maintainer permissions
   - Automatically cloned repositories, injected payload, incremented version
   - Self-propagated to 160+ additional packages using stolen credentials

4. **Legitimacy Bypass:**
   - All malicious packages have **valid SLSA Build Level 3 provenance**
   - Signatures are cryptographically correct (signed by legitimate CI)
   - Traditional supply chain security tools marked packages as "safe"

### Why This Attack is Significant

1. **SLSA Provenance Bypass:** First attack showing SLSA attestations can be legitimately signed for malicious packages
2. **CI/CD Compromise:** Attack didn't steal credentials; it hijacked the legitimate build pipeline
3. **Self-Propagation:** Worm behavior across package ecosystems
4. **Scale:** 169 packages across multiple high-profile organizations
5. **Speed:** 6-minute attack window for initial compromise

---

## Detection Indicators

**Check for compromise if:**

✅ Any `npm install` ran on May 11-12, 2026  
✅ Systems have any @tanstack/*, @mistralai/*, @uipath/*, @squawk/* packages  
✅ package-lock.json shows versions matching malicious ranges  
✅ Unexpected npm registry traffic to malicious versions  
✅ Unexpected GitHub token usage or repository access  
✅ Cloud credential anomalies (AWS, Azure, GCP)  
✅ Cryptocurrency wallet access from unexpected IPs  

**Network Indicators:**
- Exfiltration to attacker-controlled GitHub repositories
- Unusual npm registry requests for affected packages
- HTTP POST to unknown domains with credential-like payloads

---

## Remediation

**If compromised:**

1. **🔴 CRITICAL - Assume full environment compromise**
2. **🔄 Rotate ALL credentials immediately:**
   - GitHub tokens and SSH keys
   - npm credentials
   - Cloud provider keys (AWS, Azure, GCP)
   - Any secrets accessible from environment
   - Cryptocurrency wallet seeds (transfer to new wallet immediately)

3. **🔍 Audit for persistence:**
   - Check for backdoor accounts
   - Review SSH authorized_keys
   - Scan for web shells or cron jobs
   - Review GitHub repository webhooks and deploy keys

4. **🧹 Clean and rebuild:**
   - Remove all node_modules directories
   - Update package.json to safe versions
   - Run `npm ci` with lockfile using only safe versions
   - Consider rebuilding compromised systems from clean images

5. **📊 Investigate:**
   - Review logs for exfiltration activity
   - Check for lateral movement
   - Identify all affected systems and accounts

---

## Prevention Recommendations

**GitHub Actions Security:**
1. ❌ Avoid `pull_request_target` unless absolutely necessary
2. ✅ Use `pull_request` event for most workflows
3. ✅ Never checkout fork code with write permissions
4. ✅ Review all cache usage in workflows
5. ✅ Implement strict OIDC token scoping

**Supply Chain Security:**
1. ✅ Pin all dependencies to exact versions (not ranges)
2. ✅ Use lockfiles (package-lock.json, pnpm-lock.yaml)
3. ✅ Enable npm audit in CI/CD pipelines
4. ✅ Monitor for unexpected dependency updates
5. ✅ Use private npm registry mirrors for critical projects
6. ⚠️ Don't trust SLSA provenance alone (this attack proves it can be legitimate but malicious)

**Detection:**
1. ✅ Implement continuous dependency monitoring
2. ✅ Alert on unexpected package version changes
3. ✅ Monitor CI/CD logs for anomalies
4. ✅ Use automated scanners like this toolchain-checker
5. ✅ Subscribe to security advisories (npm, GitHub, GHSA)

---

## Resources & References

- **CVE-2026-45321:** TanStack Supply Chain Compromise
- **GitHub Advisory:** [GHSA-g7cv-rxg3-hmpx](https://github.com/advisories/GHSA-g7cv-rxg3-hmpx)
- **TanStack Postmortem:** [tanstack.com/blog/npm-supply-chain-compromise-postmortem](https://tanstack.com/blog/npm-supply-chain-compromise-postmortem)
- **Attack Analysis:** [landh.tech/blog/20260511-tanstack-supply-chain-compromise](https://www.landh.tech/blog/20260511-tanstack-supply-chain-compromise/)
- **Aikido Security:** [Mini Shai-Hulud Is Back](https://www.aikido.dev/blog/mini-shai-hulud-is-back-tanstack-compromised)
- **StepSecurity Analysis:** [TeamPCP's Mini Shai-Hulud Is Back](https://www.stepsecurity.io/blog/mini-shai-hulud-is-back-a-self-spreading-supply-chain-attack-hits-the-npm-ecosystem)
- **Snyk Report:** [TanStack npm Packages Hit by Mini Shai-Hulud](https://snyk.io/blog/tanstack-npm-packages-compromised/)

---

## Next Steps

1. **Obtain GitHub Token:**
   ```bash
   # Create at https://github.com/settings/tokens
   # Required scope: public_repo
   echo "YOUR_TOKEN" > .github_token
   ```

2. **Run Automated Scans:**
   ```bash
   # Comprehensive GitHub scan (~10-15 min with token)
   python3 scripts/scan_github.py

   # OBS package scan (~5-10 min)
   python3 scripts/scan_obs.py

   # Quick TanStack-specific scan
   python3 scripts/scan_tanstack.py
   ```

3. **Generate Summary Reports:**
   ```bash
   # Results will be saved to reports/ directory
   # Markdown summaries created automatically
   ```

4. **Manual Verification of High-Risk Repos:**
   - Rancher Dashboard UI
   - SUSE AI repositories
   - Uyuni web components

---

**Report Generated:** May 12, 2026  
**Scanner Version:** 2.0 (TanStack/Mini Shai-Hulud)  
**Status:** Awaiting GitHub token for automated scanning  
**Recommendation:** Proceed with manual high-priority checks while setting up token
