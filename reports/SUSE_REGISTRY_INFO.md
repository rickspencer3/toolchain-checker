# SUSE Container Registry Scanning

## Overview

**Registry URL:** https://registry.suse.com  
**API Endpoint:** https://registry.suse.com/v2/  
**Web Catalog:** https://registry.suse.com/repositories

The SUSE Container Registry hosts official SUSE container images, including:
- **Base Container Images (BCI)** - SUSE Linux Enterprise base images
- **Development containers** - Python, Java, Node.js, Go, Rust, PHP, Ruby, .NET, C++
- **Runtime containers** - Lightweight runtime versions
- **Application containers** - Pre-built solutions (RMT, MCP servers, etc.)

## Why Scan Container Images?

Container images may contain:
- Python packages (via pip/requirements.txt)
- npm packages (via npm/package.json)
- Other dependencies installed during image build

These dependencies could include compromised packages from supply chain attacks.

## Scanner Implementation

**Tool:** `scripts/scan_suse_registry.py`

### Prerequisites

1. **Docker or Podman** (required to pull and inspect images)
   ```bash
   # Install Docker
   sudo zypper install docker
   sudo systemctl start docker
   sudo usermod -aG docker $USER  # Add yourself to docker group
   
   # OR install Podman
   sudo zypper install podman
   ```

2. **Authentication** (optional, but recommended for full access)
   - SUSE customer credentials
   - OR service account credentials
   - Set via environment variables:
     ```bash
     export REGISTRY_USERNAME='your-username'
     export REGISTRY_PASSWORD='your-password'
     ```

3. **Disk Space**
   - Container images can be large (500MB - 2GB each)
   - Ensure sufficient disk space for pulling images

### How It Works

1. **Authenticate** with registry.suse.com (optional)
2. **List repositories** via Docker Registry API v2
3. **Get image tags** for each repository
4. **Pull container image** using Docker/Podman
5. **Extract dependency files** from container filesystem:
   - `/requirements.txt`
   - `/app/requirements.txt`
   - `/package.json`
   - `/app/package.json`
   - And other common locations
6. **Parse dependencies** and check against compromised packages database
7. **Report findings**

### Usage

**Basic scan (anonymous access):**
```bash
python3 scripts/scan_suse_registry.py
```

**Authenticated scan (full access):**
```bash
export REGISTRY_USERNAME='your-suse-username'
export REGISTRY_PASSWORD='your-password'
python3 scripts/scan_suse_registry.py
```

**Cleanup after scan:**
```bash
# Remove pulled images to free disk space
docker image prune -a
# or
podman image prune -a
```

## Known Container Repositories

As of May 2, 2026:

### Python Containers
- `bci-python314` - Python 3.14 micro runtime
- `bci-python313` - Python 3.13 development container
- `bci-python311` - Python 3.11 development container

### Java Containers
- `bci-openjdk25-devel` - OpenJDK 25 development
- `bci-openjdk25` - OpenJDK 25 runtime
- `bci-openjdk-devel21` - OpenJDK 21 development
- `bci-openjdk21` - OpenJDK 21 runtime

### Application Containers
- `rmt` - SUSE Repository Mirroring Tool
- `suse-agentic-mcp-multi-linux-manager` - MCP server for system management

### Other
- SUSE Linux Enterprise Server base images
- Language-specific development and runtime images
- Third-party certified images

*Full list available at: https://registry.suse.com/repositories*

## Registry API

The registry implements **Docker Registry API v2**:

### Endpoints

**Check API availability:**
```bash
curl https://registry.suse.com/v2/
# Response: {"errors":[{"code":"UNAUTHORIZED","message":"authentication required"}]}
```

**List repositories (requires auth):**
```bash
curl -u username:password https://registry.suse.com/v2/_catalog
# Response: {"repositories":["repo1","repo2",...]}
```

**List image tags:**
```bash
curl -u username:password https://registry.suse.com/v2/<repo>/tags/list
# Response: {"name":"<repo>","tags":["latest","1.0","1.1",...]}
```

**Pull image manifest:**
```bash
curl -u username:password https://registry.suse.com/v2/<repo>/manifests/<tag>
```

## Integration with Toolchain Checker

The SUSE Container Registry scanner is integrated into the toolchain-checker project:

**Attack Database:** Uses `scripts/compromised_packages.json`  
**Results Location:** `reports/registry_scan_YYYYMMDD_HHMMSS.json`  
**Log Location:** `log/toolchain_checker.log`

## Limitations

1. **Requires Docker/Podman** - Cannot scan without container runtime
2. **Authentication may be required** - Some images need SUSE customer credentials
3. **Disk space intensive** - Each image pull requires hundreds of MB
4. **Time consuming** - Pulling and inspecting images is slower than GitHub/OBS scans
5. **Dependency file discovery** - May miss dependencies in non-standard locations

## Recommendations

### For Scheduled Scans

**Strategy 1: Selective scanning**
- Only scan Python and Node.js containers (most likely to have PyPI/npm dependencies)
- Focus on recently updated images
- Use web catalog to filter by language

**Strategy 2: Full scan**
- Scan all repositories once per week
- Use incremental scanning (only new/updated images)
- Schedule during low-usage hours due to disk I/O

### For Incident Response

When a new supply chain attack is discovered:

1. **Identify affected ecosystems** (npm, PyPI, etc.)
2. **Filter containers by language** (Python containers for PyPI, Node.js for npm)
3. **Priority scan AI/ML containers** (for Python attacks like pytorch-lightning)
4. **Scan recently built images** (check build dates via manifest)

## Resources

- [SUSE Container Images Catalog](https://registry.suse.com/)
- [SUSE Container Guide](https://documentation.suse.com/container/all/pdf/Container-guide_en.pdf)
- [Docker Registry API v2 Specification](https://docs.docker.com/registry/spec/api/)
- [SUSE Container Documentation](https://documentation.suse.com/container/)

---

**Last Updated:** May 2, 2026  
**Scanner Status:** Implemented, not yet executed  
**Next Steps:** Install Docker/Podman and run initial scan
