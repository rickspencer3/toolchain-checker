# GitHub Token Setup for Toolchain Checker

## Recommended: Fine-Grained Token (Read-Only)

**Most secure option with read-only access**

### Steps:

1. **Create token:**
   - Go to: https://github.com/settings/tokens?type=beta
   - Click: "Generate new token"
   - Name: `toolchain-checker-read-only`
   - Expiration: 90 days (or your preference)

2. **Configure Repository Access:**
   - Select: "Public Repositories (read-only)"
   - Optional: Restrict to specific organizations (SUSE, Rancher, openSUSE, uyuni-project)

3. **Set Permissions (all read-only):**
   - **Contents**: Read-only ✓
   - **Metadata**: Read-only ✓ (auto-selected)
   
   That's it! No other permissions needed.

4. **Generate and save:**
   ```bash
   # Save to .github_token file
   echo "github_pat_YOUR_TOKEN_HERE" > .github_token
   chmod 600 .github_token  # Restrict permissions
   ```

5. **Add to .gitignore:**
   ```bash
   echo ".github_token" >> .gitignore
   ```

### Benefits:
- ✅ True read-only access (cannot modify anything)
- ✅ Scoped to specific organizations
- ✅ Auto-expires (prevents stale tokens)
- ✅ Detailed audit logs
- ✅ 5,000 requests/hour rate limit
- ✅ Even if leaked, attacker can only read public data (already public)

---

## Alternative: Classic Token (Less Secure)

**Simpler setup, but grants write access**

### Steps:

1. **Create token:**
   - Go to: https://github.com/settings/tokens
   - Click: "Generate new token (classic)"
   - Note: `toolchain-checker`
   - Expiration: 90 days

2. **Select scopes:**
   - ☑️ `public_repo` - Access public repositories
   - ⚠️ **Warning:** This grants READ AND WRITE access to public repos

3. **Generate and save:**
   ```bash
   echo "ghp_YOUR_TOKEN_HERE" > .github_token
   chmod 600 .github_token
   ```

### Limitations:
- ⚠️ Grants write access (can modify public repos, create issues/PRs)
- ⚠️ Cannot scope to specific organizations
- ⚠️ No auto-expiration (must manually set)
- ✅ Cannot access private repositories
- ✅ 5,000 requests/hour rate limit

---

## Security Best Practices

1. **Restrict file permissions:**
   ```bash
   chmod 600 .github_token  # Only owner can read
   ```

2. **Add to .gitignore:**
   ```bash
   # Prevent accidental commits
   echo ".github_token" >> .gitignore
   ```

3. **Set expiration:**
   - Recommended: 90 days or less
   - Rotate regularly

4. **Audit token usage:**
   - Check: https://github.com/settings/tokens
   - Review: "Last used within the last X days"
   - Revoke if suspicious activity

5. **Revoke if compromised:**
   - Go to: https://github.com/settings/tokens
   - Click "Delete" next to compromised token
   - Generate new token immediately

6. **Monitor for leaks:**
   ```bash
   # GitHub automatically scans for leaked tokens
   # If detected, GitHub will auto-revoke and notify you
   ```

---

## What the Scanner Can Access

**With read-only fine-grained token:**
- ✅ List public repositories in organizations
- ✅ Read file contents (package.json, requirements.txt)
- ✅ List branches
- ✅ Search code (Code Search API)
- ✅ Read commit history
- ❌ Cannot modify any repositories
- ❌ Cannot access private repositories
- ❌ Cannot create issues/PRs
- ❌ Cannot access organization secrets

**With `public_repo` classic token:**
- ✅ All of the above
- ⚠️ CAN modify public repositories (create/edit/delete files)
- ⚠️ CAN create issues and pull requests
- ⚠️ CAN manage collaborators on public repos
- ❌ Cannot access private repositories

---

## For SUSE Use Case

**Recommended configuration:**

1. **Token type:** Fine-grained personal access token
2. **Access:** Public repositories (read-only)
3. **Organizations:** SUSE, Rancher, openSUSE, uyuni-project, SUSE-Rancher-Community
4. **Permissions:**
   - Contents: Read-only
   - Metadata: Read-only
5. **Expiration:** 90 days
6. **Storage:** `.github_token` file with chmod 600

**Why this is safe:**
- Only reads data that's already public
- Cannot modify any repositories
- Cannot access private/internal SUSE code
- Auto-expires to prevent stale credentials
- If leaked, worst case: attacker reads public repos (already accessible)

---

## Testing Your Token

After creating the token:

```bash
# Test basic API access
curl -H "Authorization: token $(cat .github_token)" \
  https://api.github.com/user

# Check rate limit (should show 5000/hour)
curl -H "Authorization: token $(cat .github_token)" \
  https://api.github.com/rate_limit

# Test repository access
curl -H "Authorization: token $(cat .github_token)" \
  https://api.github.com/orgs/SUSE/repos?per_page=1
```

Expected rate limit with token:
```json
{
  "resources": {
    "core": {
      "limit": 5000,
      "remaining": 5000
    }
  }
}
```

---

## Troubleshooting

**"Bad credentials" error:**
- Token may be expired
- Token may be revoked
- Check token format (starts with `github_pat_` or `ghp_`)

**Rate limit still 60/hour:**
- Token not loaded properly
- Check file permissions (`ls -la .github_token`)
- Verify token in file (`head .github_token`)

**"Resource not accessible by personal access token":**
- Token doesn't have required permissions
- For fine-grained: Add "Contents: Read" permission
- For classic: Need `public_repo` scope

---

## Quick Setup (Recommended)

```bash
# 1. Create fine-grained token at:
#    https://github.com/settings/tokens?type=beta
#    - Public repos (read-only)
#    - Contents: Read, Metadata: Read
#    - Expiration: 90 days

# 2. Save token
echo "github_pat_YOUR_TOKEN_HERE" > .github_token
chmod 600 .github_token

# 3. Add to .gitignore
echo ".github_token" >> .gitignore

# 4. Test
python3 scripts/scan_github.py

# 5. Expected scan time: 10-15 minutes (vs 6-8 hours without token)
```

---

**Summary:** Use fine-grained read-only token for maximum security. It's safer, more granular, and provides the same functionality as classic `public_repo` token without write access.
