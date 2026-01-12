---
name: git-security-cleanup
description: This skill handles Git security cleanup operations including removing sensitive information from commit history, configuring .gitignore, creating secure configuration templates, and managing API key protection for repositories.
---

# Git Security Cleanup Skill

This skill handles Git security operations to prevent and fix sensitive information leaks in Git repositories.

## When to Use This Skill

Use this skill when:
- Preparing to push a new Git repository to public platforms (GitHub, GitLab, etc.)
- Realizing sensitive information (API keys, passwords, tokens) has been committed to Git history
- Need to secure a repository with proper .gitignore configuration
- Want to create configuration template files without exposing sensitive data
- Need to audit and clean Git history for secrets

## Core Workflows

### Workflow 1: Initial Repository Security Setup

Before pushing any repository to a public platform:

1. **Scan for sensitive information:**
   ```bash
   # Check for API keys
   grep -r "sk-[a-zA-Z0-9]{20,}" .
   grep -r "api_key.*=" .
   grep -r "password\|passwd\|secret\|token" .
   ```

2. **Configure .gitignore:**
   - Add all sensitive files to `.gitignore`
   - Include API key files, config files with secrets, environment variables
   - Use example files as exceptions (e.g., `!.streamlit/secrets.toml.example`)

3. **Create configuration templates:**
   - Copy sensitive files with `.example` suffix
   - Replace all real values with placeholders (e.g., `your-api-key-here`)
   - Document how users should set up their local configuration

4. **Verify before commit:**
   ```bash
   git add .
   git status  # Review staged files
   git diff --cached  # Review actual changes
   git commit -m "Commit message"
   ```

### Workflow 2: Cleaning Committed Secrets

#### Scenario A: Sensitive info in latest commit (minor issue)

1. Modify the file to remove sensitive data
2. Amend the commit:
   ```bash
   git add <modified-file>
   git commit --amend
   git push -f origin <branch-name>
   ```

#### Scenario B: Sensitive info in multiple commits (major issue)

1. Create a clean root commit:
   ```bash
   git checkout --orphan new-root
   git add .
   git commit -m "Clean initial commit"
   ```

2. Replace the main branch:
   ```bash
   git branch -D main
   git branch -m new-root main
   ```

3. Force push to update remote history:
   ```bash
   git push -f origin main
   ```

4. Verify remote repository is clean

### Workflow 3: Sensitive Information Audit

Perform comprehensive audit of repository:

1. **Check commit history:**
   ```bash
   git log --all --oneline
   git show <commit-hash>:<file>  # Inspect files in commits
   ```

2. **Search for patterns:**
   - API keys: `sk-`, `dtn_`, `eyJ` (JWT)
   - Passwords: `password`, `passwd`
   - Secrets: `secret`, `token`, `credential`
   - Database strings: `mongodb://`, `mysql://`, `postgres://`

3. **Review .gitignore effectiveness:**
   ```bash
   git check-ignore -v <file>  # Verify ignore rules
   ```

4. **Generate security report:**
   - List all findings
   - Categorize by severity
   - Provide remediation steps

### Workflow 4: Post-Cleanup Verification

After cleaning sensitive information:

1. **Verify remote repository:**
   - Check GitHub/GitLab repository
   - Review commit history
   - Inspect sensitive files (should not exist)

2. **Create security documentation:**
   - Document what was cleaned
   - List removed sensitive items
   - Provide setup instructions for new users

3. **Team notification:**
   - Inform all collaborators about history rewrite
   - Instruct them to force pull: `git fetch --all && git reset --hard origin/main`

## Reusable Resources

### Scripts

No scripts included - all operations use standard Git commands.

### References

Key patterns to identify sensitive information:

**API Keys:**
- OpenAI: `sk-[a-zA-Z0-9]{20,}`
- DeepSeek: `sk-[a-zA-Z0-9]{20,}`
- Daytona: `dtn_[a-zA-Z0-9]{40,}`
- JWT: `eyJ[a-zA-Z0-9_-]{100,}`

**Common Sensitive Files:**
- `.env`, `.env.local`, `.env.production`
- `secrets.yaml`, `config/secret.yaml`
- `.streamlit/secrets.toml`
- `credentials.json`, `service-account.json`
- `id_rsa`, `*.pem`, `*.key`
- `.aws/credentials`

### Assets

None required for this skill.

## Security Best Practices

### Before Committing
- Always check `git diff --cached` before committing
- Use environment variables for credentials
- Never commit files with real API keys
- Keep `.gitignore` up to date

### Code Level
```python
# Bad: Hardcoded secrets
API_KEY = "sk-real-key-here"
DB_PASSWORD = "my-password-123"

# Good: Environment variables
import os
API_KEY = os.environ.get("API_KEY")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
```

### Configuration Files
- Separate configuration into public and private files
- Use `.example` files for public templates
- Document required environment variables in README

### Git Hooks (Optional)
Set up pre-commit hooks to prevent accidental commits:

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check for API keys
if git diff --cached | grep -E "sk-[a-zA-Z0-9]{20,}"; then
    echo "Error: Commit contains API key"
    exit 1
fi

# Check for passwords
if git diff --cached | grep -i "password.*="; then
    echo "Error: Commit contains password"
    exit 1
fi
```

## Tool Integration

This skill uses these tools:
- `git` - All Git operations
- `grep` - Searching for patterns
- `sed` - Text replacement (if needed)

No additional tool setup required.

## Common Commands Reference

```bash
# Initialize repo
git init

# Check status
git status
git log --oneline

# Stage files
git add .
git add <file>

# Commit
git commit -m "message"
git commit --amend

# Branch operations
git branch -D <branch>
git branch -m <new-name>
git checkout --orphan <new-branch>

# Push operations
git push origin <branch>
git push -f origin <branch>  # Force push (use with caution)

# Remote operations
git remote add origin <url>
git remote -v

# Inspection
git show <commit>:<file>
git diff --cached
git check-ignore -v <file>
```

## Error Handling

### Force Push Fails
**Error**: `! [rejected] main -> main (fetch first)`

**Solution**: Use `-f` flag for force push
```bash
git push -f origin main
```

### Still Seeing Secrets After Cleanup
**Cause**: Secrets may be in multiple branches or tags

**Solution**: Clean all refs
```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch sensitive.txt" \
  --prune-empty --tag-name-filter cat -- --all
git push -f origin --all
git push -f origin --tags
```

### .gitignore Not Working
**Cause**: File was already committed before adding to .gitignore

**Solution**: Remove from Git index first
```bash
git rm --cached <file>
git commit -m "Remove sensitive file from index"
```

## Completion Checklist

When finishing Git security cleanup:

- [ ] All sensitive files removed from repository
- [ ] .gitignore properly configured
- [ ] Configuration templates created (.example files)
- [ ] Git history cleaned (no sensitive commits)
- [ ] Force pushed to remote (if history rewritten)
- [ ] Team notified (if applicable)
- [ ] Security report generated
- [ ] Verified remote repository is clean
