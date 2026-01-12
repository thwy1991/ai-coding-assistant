# Git Security Skill 使用说明

## 概述

`git-security-cleanup` skill 提供了一套完整的Git安全清理和防护工具，用于防止和修复Git仓库中的敏感信息泄露。

## Skill 结构

```
git-security-cleanup/
├── SKILL.md                          # 主要技能文档
├── references/
│   └── gitignore-template.md           # .gitignore 配置模板
└── scripts/
    ├── scan_secrets.py                 # 敏感信息扫描工具
    └── clean_history.py                # Git历史清理工具
```

## 功能模块

### 1. 敏感信息扫描 (scan_secrets.py)

扫描项目中是否包含敏感信息。

**检测内容:**
- API密钥 (OpenAI, DeepSeek, Daytona等)
- JWT令牌
- 数据库连接字符串
- 密码和密钥
- SSH私钥和证书

**使用方法:**
```bash
# 扫描当前目录
python .codebuddy/skills/git-security-cleanup/scripts/scan_secrets.py

# 扫描指定目录
python .codebuddy/skills/git-security-cleanup/scripts/scan_secrets.py /path/to/project
```

**输出示例:**
```
🔍 扫描目录: .

⚠️ 发现敏感信息！

📄 文件: config.yaml
  • 类型: Password Assignment
    行号: 15
    内容: password = "my-secret-password-123"

📄 文件: .streamlit/secrets.toml
  • 类型: DeepSeek API Key
    行号: 12
    内容: sk-abc123def456...
```

### 2. Git历史清理 (clean_history.py)

自动清理Git历史中的敏感信息，创建干净的新历史。

**使用场景:**
- 发现已将敏感信息提交到Git历史
- 需要重写Git仓库历史
- 准备将仓库发布到公开平台

**使用方法:**
```bash
python .codebuddy/skills/git-security-cleanup/scripts/clean_history.py
```

**执行流程:**
1. 检查是否在Git仓库中
2. 检查未提交的更改
3. 创建新的干净根提交
4. 替换主分支
5. 强制推送到远程仓库
6. 验证清理结果

**重要提示:**
- 此操作会重写Git历史
- 所有协作者需要强制拉取
- 需要确认操作才能执行强制推送

### 3. .gitignore 配置模板

提供完整的 .gitignore 配置模板。

**使用方法:**
```bash
# 复制模板到项目根目录
cp .codebuddy/skills/git-security-cleanup/references/gitignore-template.md .gitignore

# 根据项目需求自定义
vim .gitignore
```

**包含模式:**
- 环境变量文件 (.env, .env.local)
- API密钥文件 (secrets.yaml, credentials.json)
- SSH密钥和证书 (*.pem, *.key)
- 配置示例文件的例外规则 (!.env.example)

## 使用场景

### 场景1: 新项目准备发布

在推送新项目到GitHub前:

```bash
# 1. 扫描敏感信息
python .codebuddy/skills/git-security-cleanup/scripts/scan_secrets.py

# 2. 检查.gitignore
cat .gitignore

# 3. 创建配置模板
cp config/secret.yaml config/secret.yaml.example
# 编辑example文件，移除真实值

# 4. 提交
git add .
git commit -m "Initial commit"
git push origin main
```

### 场景2: 发现已提交敏感信息

如果发现敏感信息已提交到Git历史:

```bash
# 1. 修改文件，移除敏感信息
vim config.yaml  # 将 api_key 改为 ""

# 2. 如果只是最近一次提交，使用 amend
git add config.yaml
git commit --amend
git push -f origin main

# 3. 如果多次提交包含敏感信息，使用清理工具
python .codebuddy/skills/git-security-cleanup/scripts/clean_history.py
```

### 场景3: 团队协作安全

确保团队环境的安全:

```bash
# 1. 提供配置模板
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# 2. 在README中说明
echo "复制 .streamlit/secrets.toml.example 并填入你的API密钥" >> README.md

# 3. 将模板加入 .gitignore
echo ".streamlit/secrets.toml" >> .gitignore

# 4. 提交配置
git add .gitignore .streamlit/secrets.toml.example README.md
git commit -m "Add security configuration"
git push
```

## 最佳实践

### 开发阶段
1. 使用环境变量存储敏感信息
2. 从不将真实密钥硬编码到代码中
3. 定期运行 `scan_secrets.py` 检查

### 提交前检查
```bash
# 查看暂存区更改
git diff --cached

# 扫描敏感信息
python .codebuddy/skills/git-security-cleanup/scripts/scan_secrets.py

# 确认后提交
git commit -m "Message"
```

### 发布前审计
```bash
# 完整扫描
python .codebuddy/skills/git-security-cleanup/scripts/scan_secrets.py

# 检查历史
git log --all --oneline

# 验证敏感文件被忽略
git check-ignore -v .streamlit/secrets.toml
```

### 紧急响应
如果发现已泄露敏感信息:
1. 立即撤销或删除仓库访问
2. 轮换所有已泄露的密钥
3. 使用 `clean_history.py` 清理历史
4. 通知所有协作者强制拉取
5. 发布安全事件报告

## 集成到工作流

### 作为Git Hook (可选)

创建 `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# 提交前自动扫描

python .codebuddy/skills/git-security-cleanup/scripts/scan_secrets.py

if [ $? -ne 0 ]; then
    echo "⚠️ 发现敏感信息，提交已中止"
    exit 1
fi
```

### CI/CD 集成

在GitHub Actions中添加安全检查:

```yaml
- name: Security Scan
  run: |
    python .codebuddy/skills/git-security-cleanup/scripts/scan_secrets.py
```

## 故障排查

### scan_secrets.py 返回误报

**原因**: 模式过于宽泛

**解决**: 编辑脚本中的 `SENSITIVE_PATTERNS` 字典，调整正则表达式

### clean_history.py 推送失败

**原因**: 权限不足或网络问题

**解决**:
1. 检查GitHub令牌权限
2. 确认远程仓库URL正确
3. 手动执行: `git push -f origin main`

### .gitignore 不生效

**原因**: 文件已在提交中

**解决**:
```bash
git rm --cached sensitive-file
git commit -m "Remove sensitive file from index"
```

## 相关资源

- **规则文档**: `C:\Users\DELL\.codebuddy\rules\git-security.mdc`
- **主文档**: `docs/GIT_SECURITY_SKILL.md`
- **Skill文件**: `.codebuddy/skills/git-security-cleanup/SKILL.md`

## 更新日志

- **v1.0** (2026-01-12)
  - 初始版本
  - 敏感信息扫描功能
  - Git历史清理功能
  - .gitignore 配置模板
