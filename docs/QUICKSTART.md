# 快速入门指南

## 5分钟上手AI Coding Assistant

### 步骤1：安装依赖（1分钟）

```bash
cd ai_coding
pip install -r requirements.txt
```

### 步骤2：启动应用（10秒）

```bash
streamlit run src/ai_coding/frontend/streamlit_app.py
```

浏览器会自动打开 http://localhost:8501

### 步骤3：选择模型和执行模式（30秒）

在左侧边栏：

**选择模型：**
1. 点击"模型系列"下拉框
2. 选择一个模型（如DeepSeek）
3. 选择具体模型（如deepseek-chat）
4. 输入API密钥（如需要）
5. 点击"切换模型"

**选择执行模式：**
1. 在"代码执行方式"下拉框选择模式：
   - **auto**: 自动选择（优先Docker，推荐）
   - **local**: 本地执行（速度快）
   - **docker**: Docker容器（安全隔离）
   - **daytona**: 云端沙箱（最高安全）
2. 勾选"🚀 代码生成后自动执行"可自动执行生成的代码

> 💡 **提示**：
> - 如果不配置API密钥，会自动使用Mock模式返回示例代码
> - 选择"auto"模式会优先使用Docker，不可用时降级到本地
> - Daytona模式需要额外配置API密钥，详见 [DAYTONA.md](./DAYTONA.md)

### 步骤4：开始使用（3分钟）

#### 生成并自动执行代码

在对话框输入：
```
写一个Python函数计算斐波那契数列
```

AI会：
1. 生成代码
2. 自动在选择的执行模式中运行
3. 显示执行结果

#### 手动编辑和执行

1. 在左侧"代码编辑区"可以编辑生成的代码
2. 点击"▶️ 执行当前代码"按钮手动执行
3. 查看输出结果或错误信息

#### 保存文件

1. 点击"💾 保存到文件"按钮
2. 输入文件名
3. 文件会保存到workspace目录

### 配置API密钥（可选）

#### 方式1：环境变量（推荐）

```bash
# Linux/Mac
export OPENAI_API_KEY="sk-..."

# Windows PowerShell
$env:OPENAI_API_KEY="sk-..."
```

#### 方式2：在页面中配置

1. 在左侧边栏选择模型
2. 在"API密钥"输入框粘贴密钥
3. 点击"切换模型"

#### 方式3：编辑配置文件

编辑 `.streamlit/secrets.toml`：
```toml
OPENAI_API_KEY = "sk-..."
```

然后重启应用。

## 常用功能

### 1. 切换编程语言

在左侧边栏选择：
- Python
- JavaScript
- Java
- Go
- Rust
- Bash
- C/C++

### 2. 自动调试

当代码执行出错时：
1. 系统会显示错误信息
2. 点击"🔧 自动修复"按钮
3. AI会自动分析并修复代码

### 3. 代码优化

点击"⚡ 优化代码"按钮，AI会优化代码性能。

### 4. 生成测试

点击"🧪 生成测试"按钮，AI会生成单元测试。

### 5. 切换模型

随时可以在左侧边栏切换不同的AI模型，比如：
- GPT-4 → 通用代码生成
- DeepSeek Coder → 代码优化
- Claude → 代码审查

## 示例场景

### 场景1：学习新语言

```
用户：我刚开始学Go，写一个Hello World程序
AI：[生成Go代码]

用户：解释一下这段代码
AI：[详细解释代码功能]
```

### 场景2：算法实现

```
用户：实现快速排序算法
AI：[生成Python快速排序代码]

用户：测试这段代码
AI：[生成测试用例]
```

### 场景3：调试bug

```
用户：[粘贴有错误的代码]
AI：分析错误...

用户：帮我修复
AI：[自动修复代码]
```

### 场景4：性能优化

```
用户：[粘贴代码]
AI：这段代码可以优化吗？

用户：优化它
AI：[优化后的代码]
```

## 快捷键

- `Ctrl + Enter` - 提交消息
- `Tab` - 缩进
- `Shift + Tab` - 取消缩进

## 下一步

- 📖 查看完整文档：[README.md](../README.md)
- 🤖 了解模型配置：[MODELS.md](./MODELS.md)
- ⚙️ 查看配置指南：[SETUP.md](./SETUP.md)
- 🧪 运行测试：`python tests/test_executor.py`

## 常见问题

**Q: 应用启动失败？**

A: 检查是否安装了所有依赖：
```bash
pip install -r requirements.txt
```

**Q: 没有API密钥可以用吗？**

A: 可以！使用Mock模式会返回示例代码，适合测试和演示。

**Q: 如何查看保存的文件？**

A: 文件保存在 `workspace` 目录下，可以随时查看和编辑。

**Q: 支持哪些模型？**

A: GPT-4、Claude、DeepSeek、GLM等，详见 [MODELS.md](./MODELS.md)。

**Q: 代码执行失败怎么办？**

A: 系统会自动提供"自动修复"选项，点击即可让AI帮你调试。

---

**祝使用愉快！** 🎉
