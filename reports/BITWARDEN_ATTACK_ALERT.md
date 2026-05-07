# 🚨 CRITICAL: Bitwarden CLI Supply Chain Attack

**Alert Date:** 2026-04-23 14:15 ET  
**Severity:** HIGH  
**Attribution:** TeamPCP

## Executive Summary

Bitwarden's CLI npm package was compromised through a hijacked GitHub Action in their CI/CD pipeline. The malicious version (`2026.4.0`) was distributed for approximately 1.5 hours on April 22, 2026. This is the **4th attack** attributed to TeamPCP in recent weeks.

## Attack Details

| Field | Value |
|-------|-------|
| **Package** | `@bitwarden/cli` |
| **Compromised Version** | `2026.4.0` |
| **Attack Window** | April 22, 2026 17:57 - 19:30 ET |
| **Distribution Time** | ~1.5 hours |
| **Discovery** | Socket Security, April 23, 2026 |
| **Current Status** | Malicious package removed from npm |

## Attack Vector

- **Method:** Compromised GitHub Action in Bitwarden's CI/CD pipeline
- **Payload File:** `bw1.js` (embedded in package)
- **Execution:** Runs automatically during `npm install`

## Data Exfiltration

The malicious payload steals:
- ✓ GitHub authentication tokens
- ✓ npm authentication tokens
- ✓ SSH private keys
- ✓ Crypto wallet files (MetaMask, Phantom, Solana)
- ✓ Environment variables (.env files)
- ✓ Shell history (bash/zsh)
- ✓ Cloud credentials (AWS, GCP, Azure)

**Exfiltration Methods:**
1. HTTP POST to attacker-controlled domains
2. Direct commits to GitHub repositories (persistence mechanism)

## TeamPCP Campaign Timeline

| Date | Target | Package/Tool |
|------|--------|-------------|
| March 2026 | Trivy | (Details TBD) |
| March 2026 | Checkmarx | (Details TBD) |
| March 2026 | LiteLLM | (Details TBD) |
| April 21, 2026 | General | `pgserve` (npm) |
| April 21, 2026 | General | `@automagik/genie` (npm) |
| April 22, 2026 | General | `xinference` (PyPI) |
| **April 22, 2026** | **Bitwarden** | **@bitwarden/cli** (npm) |

## Mitigation

### For Users

✅ **Safe:** Use version `2026.3.0` or earlier  
✅ **Safe:** Use official signed binaries from bitwarden.com  
❌ **UNSAFE:** Version `2026.4.0`

### For DevOps/Security Teams

1. **Scan all systems** for `@bitwarden/cli@2026.4.0`
2. **Rotate credentials** if package was installed:
   - GitHub tokens
   - npm tokens
   - SSH keys
   - Cloud provider credentials
3. **Review git history** for unauthorized commits (April 22-23)
4. **Check crypto wallets** for unauthorized access

## SUSE Impact Assessment

**Scan Status:** ⏳ IN PROGRESS

GitHub repositories being scanned for `@bitwarden/cli` dependency:
- SUSE org: Scanning...
- Rancher org: Pending
- openSUSE org: Pending

**Preliminary Results:** 4 repositories scanned, 0 affected (as of 17:25 ET)

**OBS Status:** Unlikely to be affected (Bitwarden CLI is not typically packaged in OBS)

## References

- Socket Security Blog: https://socket.dev/blog/bitwarden-cli-compromised
- The Hacker News: https://thehackernews.com/2026/04/bitwarden-cli-compromised-in-ongoing.html
- GitHub Issue (Bitwarden): https://github.com/bitwarden/clients/issues/20353
- Technical Analysis: https://gist.github.com/N3mes1s/9c210b64760390f1ca2c451100a5ec99

## Next Steps

1. ✅ Added to compromised packages database
2. ⏳ GitHub scan in progress
3. ⏳ OBS scan pending
4. ⏳ Final report generation pending

---

**Updated:** 2026-04-23 14:20 ET  
**Scan will update automatically as results come in**
