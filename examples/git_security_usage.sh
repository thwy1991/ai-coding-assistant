#!/bin/bash
# Git安全操作快速示例

echo "=========================================="
echo "Git安全操作示例"
echo "=========================================="

# 示例1: 扫描敏感信息
echo ""
echo "1. 扫描项目中的敏感信息"
echo "命令: python .codebuddy/skills/git-security-cleanup/scripts/scan_secrets.py"
echo ""

# 示例2: 清理Git历史
echo "2. 清理Git历史中的敏感信息"
echo "命令: python .codebuddy/skills/git-security-cleanup/scripts/clean_history.py"
echo "⚠️ 警告: 这会重写Git历史，请谨慎使用"
echo ""

# 示例3: 配置.gitignore
echo "3. 配置.gitignore保护敏感文件"
echo "命令: cp .codebuddy/skills/git-security-cleanup/references/gitignore-template.md .gitignore"
echo "然后根据项目需求自定义"
echo ""

# 示例4: 创建配置模板
echo "4. 创建安全的配置模板"
echo "# 示例: Streamlit配置"
echo "cp .streamlit/secrets.toml .streamlit/secrets.toml.example"
echo "vim .streamlit/secrets.toml.example  # 将真实密钥替换为占位符"
echo ""

# 示例5: 提交前检查
echo "5. 提交前的安全检查"
echo "git add ."
echo "git diff --cached  # 查看暂存的更改"
echo "python .codebuddy/skills/git-security-cleanup/scripts/scan_secrets.py  # 扫描敏感信息"
echo "git commit -m 'Safe commit message'"
echo ""

# 示例6: 验证远程仓库
echo "6. 验证远程仓库安全性"
echo "git log --oneline  # 查看提交历史"
echo "git remote -v  # 查看远程仓库"
echo "# 在GitHub上检查敏感文件是否存在"
echo ""

echo "=========================================="
echo "更多详细信息请查看:"
echo "- docs/GIT_SECURITY_SKILL.md"
echo "- .codebuddy/skills/git-security-cleanup/SKILL.md"
echo "=========================================="
