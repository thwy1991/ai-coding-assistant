# Daytona 集成指南

## 概述

AI Coding Assistant 集成了 Daytona 云端沙箱执行功能，可以在安全的云端环境中执行代码。

## Daytona 简介

Daytona 是一个开源的开发环境管理平台，提供:
- 云端代码执行沙箱
- 安全隔离的运行环境
- 支持多种编程语言
- API 集成能力

## 配置 Daytona

### 1. 获取 API 密钥

访问 [Daytona 官网](https://www.daytona.dev/) 注册账户并获取 API 密钥。

### 2. 配置方式

#### 方式一：通过 `.streamlit/secrets.toml` 配置

```toml
DAYTONA_API_KEY = "your-daytona-api-key-here"
DAYTONA_API_BASE = "https://api.daytona.dev"
```

#### 方式二：通过环境变量配置

```bash
export DAYTONA_API_KEY="your-daytona-api-key-here"
export DAYTONA_API_BASE="https://api.daytona.dev"
```

#### 方式三：通过 Streamlit 页面配置

在应用的侧边栏中选择 "daytona" 执行模式，然后输入 API 密钥。

## 执行模式说明

AI Coding Assistant 支持四种代码执行模式:

### 1. Auto 模式（自动）
- 优先使用 Docker 容器执行
- 如果 Docker 不可用，自动降级到本地执行
- **推荐**: 适合大多数场景

### 2. Local 模式（本地）
- 直接在本地环境中执行代码
- 不依赖 Docker 或外部服务
- **优点**: 速度快，无需额外配置
- **缺点**: 安全性较低，可能影响本地环境

### 3. Docker 模式
- 在 Docker 容器中隔离执行代码
- 安全性高，不影响本地环境
- **前提**: 需要安装并运行 Docker 服务
- **优点**: 隔离性好，安全性高
- **缺点**: 需要 Docker 支持

### 4. Daytona 模式（云端）
- 在 Daytona 云端沙箱中执行代码
- 完全隔离，不影响本地环境
- 需要配置 Daytona API 密钥
- **优点**: 最高安全性，无需本地 Docker
- **缺点**: 需要网络连接，可能有 API 调用费用

## 使用方法

### 在 Streamlit 页面中使用

1. 在侧边栏选择 "执行模式" 为 "daytona"
2. 输入 Daytona API 密钥和 API 地址
3. 输入代码需求，生成的代码会自动在 Daytona 云端执行
4. 或者手动编辑代码后点击 "执行当前代码" 按钮

### 代码示例

```python
# 1. 生成代码
用户输入: "写一个Python脚本计算斐波那契数列"

# 2. 代码自动在 Daytona 云端执行
# 3. 显示执行结果
```

## 支持的语言

Daytona 模式支持以下编程语言:
- Python
- JavaScript (Node.js)
- Java
- Go
- Rust
- Bash
- C/C++

## 故障排查

### 问题：Daytona API 调用失败

**错误信息**: `Daytona API错误: ...`

**解决方案**:
1. 检查 API 密钥是否正确
2. 确认账户余额是否充足
3. 检查网络连接是否正常
4. 验证 API 地址是否正确

### 问题：执行超时

**错误信息**: `执行超时（120秒）`

**解决方案**:
1. 优化代码，减少执行时间
2. 检查是否进入死循环
3. 考虑使用本地或 Docker 模式

### 问题：工作区创建失败

**错误信息**: `创建Daytona工作区失败`

**解决方案**:
1. 检查 API 权限是否允许创建工作区
2. 确认 Daytona 服务是否正常运行
3. 查看 Daytona 控制台获取详细错误信息

## API 端点说明

当前实现使用以下 Daytona API 端点:

- 创建工作区: `POST /workspaces`
- 执行代码: `POST /workspaces/{workspace_id}/execute`
- 获取工作区信息: `GET /workspaces/{workspace_id}`
- 删除工作区: `DELETE /workspaces/{workspace_id}`

## 最佳实践

1. **安全性**: 对于未知来源的代码，优先使用 Daytona 模式
2. **性能**: 对于简单的测试代码，使用 Local 模式更快
3. **隔离**: 生产环境建议使用 Docker 或 Daytona 模式
4. **成本**: 注意 Daytona API 调用费用，合理使用

## 相关文档

- [Daytona 官方文档](https://docs.daytona.dev/)
- [配置文件说明](./CONFIGURATION.md)
- [故障排查指南](./TROUBLESHOOTING.md)
