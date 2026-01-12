# AI Coding Assistant - 配置指南

本文档详细说明如何配置和运行AI Coding Assistant。

## 目录

- [依赖安装](#依赖安装)
- [API密钥配置](#api密钥配置)
- [运行应用](#运行应用)
- [常见问题](#常见问题)

---

## 依赖安装

### Python环境要求

- Python 3.8 或更高版本

### 安装步骤

```bash
# 克隆或下载项目
cd ai_coding

# 安装Python依赖
pip install -r requirements.txt
```

**主要依赖包：**
- `streamlit` - Web前端框架
- `docker` - Docker容器支持（可选）
- `openai` - OpenAI API客户端

---

## API密钥配置

### 方法1：环境变量（推荐）

#### Windows PowerShell
```powershell
$env:OPENAI_API_KEY="your-api-key-here"
```

#### Windows CMD
```cmd
set OPENAI_API_KEY=your-api-key-here
```

#### Linux/macOS
```bash
export OPENAI_API_KEY="your-api-key-here"
```

#### 永久设置（Linux/macOS）

将以下内容添加到 `~/.bashrc` 或 `~/.zshrc`：
```bash
export OPENAI_API_KEY="your-api-key-here"
```

然后执行：
```bash
source ~/.bashrc  # 或 source ~/.zshrc
```

#### 永久设置（Windows PowerShell）

```powershell
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'your-api-key-here', 'User')
```

---

### 方法2：Streamlit Secrets

1. 编辑 `.streamlit/secrets.toml` 文件

```toml
OPENAI_API_KEY = "your-api-key-here"
OPENAI_API_BASE = "https://api.openai.com/v1"
```

2. 确保文件在正确的位置：
```
ai_coding/
├── .streamlit/
│   └── secrets.toml
```

---

### 方法3：.env文件

1. 复制示例文件：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件：
```
OPENAI_API_KEY=your-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1
```

3. 应用需要从 `.env` 加载环境变量（需要在代码中添加 `python-dotenv` 支持）

---

### 获取OpenAI API密钥

1. 访问 [OpenAI官网](https://openai.com/)
2. 注册/登录账户
3. 进入 API keys 页面
4. 点击 "Create new secret key"
5. 复制生成的API密钥

---

## 运行应用

### 方式1：使用Streamlit直接运行

```bash
streamlit run src/ai_coding/frontend/streamlit_app.py
```

### 方式2：使用启动脚本

```bash
python scripts/start_app.py
```

### 方式3：使用Python模块

```bash
python -m streamlit run src/ai_coding/frontend/streamlit_app.py
```

### 访问应用

启动成功后，在浏览器中访问：
```
http://localhost:8501
```

---

## 模式说明

### Mock模式（默认）

如果未配置API密钥，应用会使用 `MockLLMClient` 返回示例代码：
- 不消耗API额度
- 返回预设的示例代码
- 适合测试和演示

### 真实AI模式

配置OpenAI API密钥后，应用会使用 `OpenAIClient`：
- 调用真实的GPT模型
- 消耗API配额
- 提供智能代码生成和调试

---

## Docker部署

### 使用Dockerfile

```bash
# 构建镜像
docker build -t ai-coding-assistant .

# 运行容器
docker run -p 8501:8501 \
  -e OPENAI_API_KEY="your-api-key-here" \
  ai-coding-assistant
```

### 使用Docker Compose

1. 编辑 `docker-compose.yml` 中的环境变量

2. 启动服务：
```bash
docker-compose up -d
```

3. 查看日志：
```bash
docker-compose logs -f
```

---

## 配置文件

### config.yaml

主要配置项：

```yaml
sandbox:
  timeout: 30              # 执行超时时间（秒）
  memory_limit: "100m"     # 内存限制
  cpu_limit: 0.5          # CPU限制
  enable_docker: true      # 是否启用Docker

llm:
  model: "gpt-4"          # 模型名称
  temperature: 0.2         # 温度参数
  max_tokens: 4096        # 最大token数

security:
  enable_sandbox: true     # 是否启用沙箱
  max_code_length: 10000  # 最大代码长度

workspace:
  base_path: "./workspace"  # 工作区路径
```

---

## 常见问题

### 1. StreamlitSecretNotFoundError

**错误信息：**
```
StreamlitSecretNotFoundError: No secrets found
```

**解决方案：**
- 确保创建了 `.streamlit/secrets.toml` 文件
- 或使用环境变量配置API密钥

---

### 2. ModuleNotFoundError: No module named 'openai'

**错误信息：**
```
ModuleNotFoundError: No module named 'openai'
```

**解决方案：**
```bash
pip install openai
```

---

### 3. Docker相关错误

**问题：** Docker未安装或未启动

**解决方案：**
- 安装 [Docker Desktop](https://www.docker.com/products/docker-desktop)
- 启动Docker服务
- 或在配置中禁用Docker，使用本地执行

---

### 4. 端口被占用

**错误信息：**
```
Address already in use
```

**解决方案：**
```bash
# 使用其他端口
streamlit run src/ai_coding/frontend/streamlit_app.py --server.port=8502
```

---

### 5. API密钥无效

**错误信息：**
```
OpenAI API error: Invalid API key
```

**解决方案：**
- 检查API密钥是否正确
- 确保API密钥没有过期
- 检查账户是否有足够的配额

---

## 开发和测试

### 运行测试

```bash
# 运行执行器测试
python tests/test_executor.py
```

### 添加新语言支持

编辑 `src/ai_coding/executor/multi_language_executor.py`，在 `SUPPORTED_LANGUAGES` 添加配置。

### 自定义LLM客户端

实现 `chat_completion` 和 `generate` 方法的类，并传递给 `AICodingWorkflow`。

---

## 安全建议

1. **不要提交API密钥到Git**
   - `.env` 文件已在 `.gitignore` 中
   - `.streamlit/secrets.toml` 也应排除

2. **使用环境变量**
   - 在生产环境推荐使用环境变量

3. **启用沙箱**
   - 保持 `security.enable_sandbox: true`

4. **限制代码执行**
   - 设置合理的 `max_code_length`

---

## 获取帮助

- 查看 [README.md](../README.md) 了解项目概览
- 提交 Issue 报告问题
- 查看源码了解实现细节
