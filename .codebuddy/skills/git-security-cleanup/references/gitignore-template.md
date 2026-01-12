# .gitignore Template for Secure Projects

## Common Patterns

### API Keys and Secrets
.env
.env.local
.env.production
.env.development
secrets.yaml
secrets.json
config/secret.yaml
config/credentials.yaml

### API-specific Files
.streamlit/secrets.toml
.aws/credentials
.google/credentials
.service-account.json
firebase-service-account.json

### SSH Keys and Certificates
*.pem
*.key
*.p12
*.pfx
id_rsa
id_rsa.pub
*.crt
*.cer

### Database Files
*.db
*.sqlite
*.sqlite3
data/

### IDE and Editor
.vscode/
.idea/
*.swp
*.swo
*~

### Python
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
env/
ENV/

### Node.js
node_modules/
npm-debug.log
yarn-error.log

### Logs
*.log
logs/
*.log.*

### OS Files
.DS_Store
Thumbs.db

## Example Files (Include These)

### Configuration Examples
!.env.example
!.streamlit/secrets.toml.example
!secrets.yaml.example
!config/credentials.yaml.example

### Template Files
!*-template.yaml
!*-template.json

## Usage Instructions

1. Copy this template to your project root as `.gitignore`
2. Customize based on your specific needs
3. Test effectiveness: `git check-ignore -v <file>`
4. Commit the `.gitignore` file to ensure security rules apply to all team members

## Best Practices

1. **Be Specific**: Use specific patterns rather than broad ignores
2. **Test Regularly**: Verify files are actually ignored
3. **Document Exceptions**: Use `!` pattern for files you DO want to include
4. **Review Before Commit**: Check `git status` before committing
5. **Keep Public**: Commit .gitignore so team members benefit from security rules
