# AI Coding Assistant

一个功能强大的AI编程助手，类似Claude Code的代码执行能力，支持多语言代码生成、执行和调试。

## 功能特性

- 🤖 **智能代码生成**: 使用大语言模型生成高质量的代码
- 🔄 **多模型支持**: 支持GPT-4、Claude、DeepSeek、GLM等多种模型
- 💻 **多语言支持**: 支持Python、JavaScript、Java、Go、Rust、Bash、C/C++等
- 🔒 **安全沙箱**: 基于Docker的隔离执行环境
- 🐛 **自动调试**: 智能检测并修复代码错误
- 📁 **项目管理**: 完整的文件系统管理
- 🛡️ **安全检查**: 代码安全扫描和风险防护
- 🎨 **Web界面**: 基于Streamlit的友好交互界面
- ⚡ **灵活配置**: 支持在页面中动态切换不同模型

## 项目结构

```
ai_coding/
├── src/
│   └── ai_coding/
│       ├── executor/          # 代码执行引擎
│       ├── generator/         # AI代码生成器
│       ├── debugger/          # 交互式调试器
│       ├── manager/           # 项目和安全管理器
│       ├── frontend/          # 前端界面
│       └── workflow.py        # 主工作流
├── docs/                      # 文档目录
├── tests/                     # 测试目录
├── scripts/                   # 脚本目录
├── workspace/                 # 工作区目录
├── config.yaml               # 配置文件
├── requirements.txt          # Python依赖
└── Dockerfile               # Docker配置
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

#### 方法1：使用环境变量（推荐）
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your-api-key-here"

# Windows CMD
set OPENAI_API_KEY=your-api-key-here

# Linux/Mac
export OPENAI_API_KEY="your-api-key-here"
```

#### 方法2：使用Streamlit secrets
编辑 `.streamlit/secrets.toml` 文件：

```toml
# OpenAI (GPT-4)
OPENAI_API_KEY = "sk-..."

# Claude
ANTHROPIC_API_KEY = "sk-ant-..."

# DeepSeek
DEEPSEEK_API_KEY = "sk-..."

# 智谱AI (GLM)
ZHIPUAI_API_KEY = "..."
```

#### 方法3：在页面中配置
启动应用后，在左侧边栏的"AI模型配置"中选择模型并输入API密钥。

#### 方法4：使用.env文件
复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```
OPENAI_API_KEY=your-api-key-here
DEEPSEEK_API_KEY=your-deepseek-key-here
ZHIPUAI_API_KEY=your-zhipuai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
```

### 3. 运行应用

```bash
streamlit run src/ai_coding/frontend/streamlit_app.py
```

或使用启动脚本：

```bash
python scripts/start_app.py
```

访问 `http://localhost:8501` 开始使用。

> **注意**: 应用启动时会使用MockLLMClient（模拟客户端），返回示例代码。如需使用真实的AI功能，请配置OpenAI API密钥并实现真实的LLM客户端。

## 使用示例

### 代码生成

```
用户：写一个Python函数计算斐波那契数列
AI：[生成代码]
```

### 代码执行

```
用户：执行刚才生成的代码
AI：[执行代码并显示输出]
```

### 自动调试

```
用户：这段代码有错误，帮我调试
AI：[自动检测错误并修复代码]
```

### 代码优化

```
用户：优化这段代码的性能
AI：[优化代码]
```

### 模型切换

在左侧边栏中：
1. 选择模型系列（GPT-4、Claude、DeepSeek、GLM）
2. 选择具体模型
3. 输入API密钥（可选）
4. 点击"切换模型"按钮

支持以下模型：
- **GPT-4**: gpt-4, gpt-4-turbo, gpt-3.5-turbo
- **Claude**: claude-3-sonnet-20240229, claude-3-haiku-20240307, claude-3-opus-20240229
- **DeepSeek**: deepseek-chat, deepseek-coder
- **GLM**: glm-4, glm-3-turbo
- **Mock**: 模拟模式，返回示例代码

## Docker部署

### 使用Docker

```bash
docker build -t ai-coding-assistant .
docker run -p 8501:8501 -e OPENAI_API_KEY=your-key ai-coding-assistant
```

### 使用Docker Compose

```bash
docker-compose up -d
```

## 配置说明

编辑 `config.yaml` 文件可以调整以下配置：

- **sandbox**: 执行沙箱设置（超时、内存限制等）
- **llm**: 大语言模型配置
- **security**: 安全检查设置
- **workspace**: 工作区路径

## 安全特性

- 🐳 Docker容器隔离
- 🔍 代码安全扫描
- 🚫 危险操作黑名单
- ⏱️ 执行超时保护
- 💾 内存限制

## 开发指南

### 添加新语言支持

在 `src/ai_coding/executor/multi_language_executor.py` 中的 `SUPPORTED_LANGUAGES` 添加新语言配置。

### 自定义LLM客户端

实现 `chat_completion` 或 `generate` 方法的客户端类，并传递给 `AICodingWorkflow`。

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 致谢

感谢所有开源项目的贡献者！
