# 故障排除指南

## 常见错误及解决方案

### 1. Docker相关错误

#### 错误信息
```
Docker不可用: Error while fetching server API version: (2, 'CreateFile', '系统找不到指定的文件。')
```

#### 原因
- Docker Desktop未安装
- Docker服务未启动
- Docker守护进程未运行

#### 解决方案

**方案1：启动Docker Desktop**
1. 打开Docker Desktop
2. 等待Docker完全启动（托盘图标变为绿色）
3. 重启应用

**方案2：安装Docker Desktop**
1. 访问 [Docker官网](https://www.docker.com/products/docker-desktop)
2. 下载并安装Docker Desktop
3. 启动Docker Desktop
4. 重启应用

**方案3：禁用Docker（使用本地执行）**
应用会自动检测到Docker不可用，并使用本地执行模式。

---

### 2. API调用错误

#### 错误信息
```
DeepSeek API调用失败: 'choices'
Claude API调用失败: 'choices'
智谱AI API调用失败: 'choices'
意图分析失败: 'choices'
代码生成失败: 'choices'
```

#### 原因
- API密钥无效或未配置
- API响应格式不符合预期
- API服务暂时不可用
- API配额不足

#### 解决方案

**方案1：检查API密钥**
1. 确认API密钥是否正确
2. 检查是否有多余的空格或特殊字符
3. 验证API密钥是否有效

**方案2：查看详细错误**
应用日志会显示具体错误信息，例如：
```
DeepSeek API错误: Incorrect API key provided
```

**方案3：检查API服务状态**
- [OpenAI状态](https://status.openai.com/)
- [Anthropic状态](https://status.anthropic.com/)
- [DeepSeek状态](https://platform.deepseek.com/)
- [智谱AI状态](https://open.bigmodel.cn/)

**方案4：检查API配额**
登录各个API提供商的控制台，检查：
- 账户余额
- 使用限额
- 月度预算

**方案5：切换到Mock模式**
如果暂时无法使用API，可以选择"Mock"模型系列，使用示例模式。

---

### 3. 网络连接错误

#### 错误信息
```
网络连接失败: Cannot connect to host
TimeoutError: Timeout connecting to API
```

#### 原因
- 网络连接问题
- 防火墙阻止
- 代理设置问题

#### 解决方案

**方案1：检查网络连接**
```bash
# Windows
ping api.openai.com

# Linux/Mac
ping api.openai.com
```

**方案2：配置代理**
设置环境变量：
```bash
# Windows
set HTTPS_PROXY=http://proxy-server:port

# Linux/Mac
export HTTPS_PROXY=http://proxy-server:port
```

**方案3：检查防火墙**
确保防火墙允许访问：
- api.openai.com
- api.anthropic.com
- api.deepseek.com
- open.bigmodel.cn

---

### 4. 依赖安装错误

#### 错误信息
```
ModuleNotFoundError: No module named 'openai'
ModuleNotFoundError: No module named 'aiohttp'
```

#### 原因
- Python依赖未安装
- 虚拟环境未激活

#### 解决方案

**安装所有依赖**
```bash
pip install -r requirements.txt
```

**单独安装缺失的包**
```bash
pip install openai aiohttp docker pyyaml streamlit
```

**使用虚拟环境**
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

---

### 5. Streamlit启动错误

#### 错误信息
```
StreamlitSecretNotFoundError: No secrets found
Address already in use
```

#### 原因
- secrets.toml文件未创建
- 端口被占用
- Streamlit版本不兼容

#### 解决方案

**创建secrets.toml**
确保文件在正确位置：
```
ai_coding/
├── .streamlit/
│   └── secrets.toml
```

**更换端口**
```bash
streamlit run src/ai_coding/frontend/streamlit_app.py --server.port=8502
```

**升级Streamlit**
```bash
pip install --upgrade streamlit
```

---

### 6. 代码执行错误

#### 错误信息
```
执行失败: ModuleNotFoundError
执行失败: NameError
执行失败: IndentationError
```

#### 原因
- 代码语法错误
- 缺少依赖库
- 逻辑错误

#### 解决方案

**方案1：使用自动修复**
执行失败后，点击"🔧 自动修复"按钮，AI会尝试修复代码。

**方案2：查看详细错误**
错误信息会显示具体原因，例如：
```
NameError: name 'math' is not defined
```

**方案3：手动修复**
根据错误信息，在代码编辑器中修复代码。

---

### 7. API配额超限

#### 错误信息
```
Quota exceeded
Rate limit exceeded
Insufficient credits
```

#### 原因
- 超出免费额度
- API调用频率超限
- 余额不足

#### 解决方案

**方案1：检查余额**
登录API提供商控制台，检查：
- 剩余额
- 使用量统计
- 配额限制

**方案2：升级套餐**
根据需要升级到付费套餐。

**方案3：切换模型**
切换到其他模型，例如：
- GPT-4 → DeepSeek（更便宜）
- Claude → GLM

---

## 调试技巧

### 启用详细日志

修改 `src/ai_coding/frontend/streamlit_app.py`，添加：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 测试API连接

使用以下测试脚本：
```python
import asyncio
from src.ai_coding.llm_clients import DeepSeekClient

async def test():
    client = DeepSeekClient(api_key="your-api-key")
    try:
        result = await client.generate("Hello")
        print(f"成功: {result}")
    except Exception as e:
        print(f"失败: {e}")

asyncio.run(test())
```

### 检查Docker状态

```bash
# Windows
docker ps

# Linux/Mac
docker ps
```

### 查看API使用量

登录各API提供商控制台查看使用统计。

---

## 获取帮助

如果问题仍未解决：

1. 查看日志文件（如果有的话）
2. 检查浏览器控制台（按F12）
3. 提交Issue到GitHub
4. 提供详细的错误信息和复现步骤

### 提交Issue时请包含

- 操作系统版本
- Python版本
- 错误信息（完整）
- 复现步骤
- 相关配置

---

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
streamlit run src/ai_coding/frontend/streamlit_app.py

# 测试执行器
python tests/test_executor.py

# 检查语法
python -m py_compile src/ai_coding/llm_clients.py

# 查看Docker状态
docker ps

# 清除缓存
streamlit cache clear
```
