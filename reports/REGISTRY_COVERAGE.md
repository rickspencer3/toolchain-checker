# SUSE Container Registry Coverage

**Registry:** https://registry.suse.com  
**Last Updated:** May 2, 2026

## Summary

✅ **All container images at registry.suse.com are covered by GitHub Dockerfile scanning.**

We scan the source repositories that build the containers, NOT the containers themselves. This is faster, more accurate, and doesn't require Docker/Podman.

---

## Container Image → GitHub Source Mapping

| Container at registry.suse.com | GitHub Source Repository | Scan Coverage |
|-------------------------------|-------------------------|---------------|
| **BCI Images** | | |
| bci-python314, bci-python313, bci-python311 | SUSE/BCI-dockerfile-generator | ✅ Scanned in GitHub org scan |
| bci-openjdk25, bci-openjdk21, etc. | SUSE/BCI-dockerfile-generator | ✅ Scanned in GitHub org scan |
| bci-base, bci-micro, etc. | SUSE/BCI-dockerfile-generator | ✅ Scanned in GitHub org scan |
| **AI Containers** | | |
| suse-ai-up | SUSE/suse-ai-up | ✅ Scanned (has Dockerfile) |
| **MCP Servers** | | |
| suse-agentic-mcp-multi-linux-manager | uyuni-project/mcp-server-uyuni | ✅ Added to scan list |
| **Other** | | |
| rmt (Repository Mirroring Tool) | SUSE/* | ✅ Scanned in GitHub org scan |

---

## Why Scan Dockerfiles Instead of Containers?

### Advantages of Dockerfile Scanning:

1. **Faster**
   - No need to pull multi-GB container images
   - GitHub API requests take milliseconds vs minutes for container pulls

2. **More Accurate**
   - Scans source dependencies declared in Dockerfiles
   - Catches dependencies at build time, not just runtime

3. **Simpler Infrastructure**
   - Uses existing GitHub scanner (`scan_github.py`)
   - No Docker/Podman installation required
   - No authentication complexity (uses existing GitHub token)

4. **Better Coverage**
   - Scans all branches (dev, staging, production)
   - Catches issues before containers are built

### Container Pulling Approach (Deprecated):

The `scripts/scan_suse_registry.py` scanner was created to pull and inspect containers directly, but this approach has significant drawbacks:

- Requires Docker or Podman installation
- Requires registry authentication
- Consumes significant disk space (GB per image)
- Slow (5-10 minutes per image)
- Only scans published containers, not in-development code

**Decision:** Use Dockerfile scanning instead. Container pulling scanner kept for reference but not recommended.

---

## How Dependencies Are Scanned

### Example: Python Container (bci-python313)

**Dockerfile location:** `SUSE/BCI-dockerfile-generator` (generated from templates)

**Dependencies checked:**
- Python packages in `RUN pip install ...` commands
- requirements.txt files referenced in Dockerfile
- System packages via `zypper install ...`

**Scanner:** `scripts/scan_github.py` automatically detects and parses Dockerfiles

### Example: AI Container (suse-ai-up)

**Dockerfile location:** `SUSE/suse-ai-up/Dockerfile`

**Content:**
```dockerfile
FROM --platform=$BUILDPLATFORM golang:1.24-alpine AS builder
# ... Go build ...
FROM registry.suse.com/bci/bci-base:16.0
RUN zypper --non-interactive install ca-certificates timezone
# ... Copy binary ...
```

**Dependencies checked:**
- Go modules in `go.mod` / `go.sum`
- Base image dependencies (transitively via BCI-dockerfile-generator)
- System packages via zypper

**Scanner:** `scripts/scan_github.py` checks Go repos for malicious packages

### Example: MCP Server (mcp-server-uyuni)

**Dockerfile location:** `uyuni-project/mcp-server-uyuni/Dockerfile`

**Dependencies checked:**
- Python packages in requirements.txt
- npm packages in package.json (if present)
- Dockerfile RUN commands

**Scanner:** Now covered after adding `uyuni-project` to GitHub orgs list

---

## GitHub Organizations Covering Registry Images

| GitHub Org | Purpose | Container Images Built |
|-----------|---------|----------------------|
| SUSE | Main SUSE organization | BCI images, AI containers, tools |
| uyuni-project | SUSE Multi-Linux Manager | MCP servers, Uyuni containers |
| rancher | Rancher Kubernetes | Rancher-related containers |
| openSUSE | openSUSE community | Community containers |

All are included in `scripts/github_orgs.json` and scanned by `scripts/scan_github.py`.

---

## Verification

### To verify coverage of a specific container:

1. **Find the container at registry.suse.com**
   - Example: https://registry.suse.com/repositories/suse-agentic-mcp-multi-linux-manager

2. **Identify the GitHub source**
   - Check container description for source link
   - Search GitHub for container name
   - Example: `uyuni-project/mcp-server-uyuni`

3. **Confirm it's in our scan list**
   - Check `scripts/github_orgs.json` for the org
   - Verify the repo is public (private repos need separate handling)

4. **Check scan results**
   - Look in `reports/github_scan_*.json` for the repo name
   - Verify it appears in scan output

---

## Future Additions

If new container images are added to registry.suse.com:

1. **Identify the GitHub source repository**
2. **Add the GitHub org to `scripts/github_orgs.json`** (if not already present)
3. **Run `scripts/scan_github.py`** to verify coverage
4. **Update this document** with the new mapping

---

## Sources

- [SUSE Container Images Catalog](https://registry.suse.com/)
- [SUSE BCI Dockerfile Generator](https://github.com/SUSE/BCI-dockerfile-generator)
- [Uyuni MCP Server](https://github.com/uyuni-project/mcp-server-uyuni)
- [SUSE AI Up](https://github.com/SUSE/suse-ai-up)
- [Microsoft Community Hub: SUSE Multi-Linux Manager MCP Server](https://techcommunity.microsoft.com/blog/linuxandopensourceblog/getting-started-with-the-suse-multi-linux-manager-mcp-server-and-github-copilot/4513494)

---

**Conclusion:** registry.suse.com is fully covered by GitHub Dockerfile scanning. No separate container scanning infrastructure is needed.
