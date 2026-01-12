# -*- coding: utf-8 -*-
"""
AI Coding Assistant - AI代码生成器
使用大语言模型生成代码
"""

import re
import json
import logging
from typing import Dict, Optional, List
import asyncio

logger = logging.getLogger(__name__)


class AICodeGenerator:
    """AI代码生成器"""

    def __init__(self, llm_client):
        """
        初始化代码生成器

        Args:
            llm_client: 大语言模型客户端
        """
        self.llm = llm_client

    async def generate_with_context(self, prompt: str, context: Dict) -> str:
        """
        带上下文的代码生成

        Args:
            prompt: 用户需求描述
            context: 上下文信息，包含language, environment, imports等

        Returns:
            str: 生成的代码
        """
        system_prompt = f"""
你是一个专业的代码助手。请生成{context.get('language', 'Python')}代码。

要求：
1. 只返回代码，不要解释
2. 如果是可执行代码，确保包含main函数或可直接执行
3. 处理可能的输入输出
4. 添加必要的错误处理

用户需求：{prompt}

执行环境：{context.get('environment', '标准环境')}
已导入的库：{', '.join(context.get('imports', []))}
"""

        try:
            response = await self._call_llm(
                system_prompt=system_prompt,
                user_message=prompt
            )

            code = self._extract_code_from_response(response)
            return code

        except Exception as e:
            logger.error(f"代码生成失败: {e}")
            return f"# 代码生成失败: {str(e)}"

    async def generate_code(self, prompt: str, language: str = 'python') -> str:
        """
        生成指定语言的代码

        Args:
            prompt: 代码需求描述
            language: 目标语言

        Returns:
            str: 生成的代码
        """
        system_prompt = f"""
你是一个专业的{language}程序员。请根据用户的需求生成高质量的{language}代码。

要求：
1. 代码应该完整且可运行
2. 包含必要的注释
3. 处理边界情况和错误
4. 遵循该语言的最佳实践
5. 只返回代码，不需要解释

用户需求：{prompt}
"""

        try:
            response = await self._call_llm(
                system_prompt=system_prompt,
                user_message=prompt
            )

            code = self._extract_code_from_response(response)
            return code

        except Exception as e:
            logger.error(f"代码生成失败: {e}")
            return f"# 代码生成失败: {str(e)}"

    async def fix_code(self, code: str, error: str, language: str = 'python') -> str:
        """
        修复代码错误

        Args:
            code: 原始代码
            error: 错误信息
            language: 代码语言

        Returns:
            str: 修复后的代码
        """
        system_prompt = f"""
你是一个专业的{language}程序员和调试专家。请分析代码并修复错误。

原代码：
```{language}
{code}
```

错误信息：
{error}

请：
1. 分析错误原因
2. 修复代码
3. 只返回修复后的完整代码，不要解释
"""

        try:
            response = await self._call_llm(
                system_prompt=system_prompt,
                user_message=f"修复以下{language}代码的错误"
            )

            fixed_code = self._extract_code_from_response(response)
            return fixed_code

        except Exception as e:
            logger.error(f"代码修复失败: {e}")
            return code  # 返回原代码

    async def analyze_error(self, code: str, error: str, language: str = 'python') -> str:
        """
        分析代码错误

        Args:
            code: 原始代码
            error: 错误信息
            language: 代码语言

        Returns:
            str: 错误分析结果
        """
        system_prompt = f"""
请分析以下{language}代码的错误：

原代码：
```{language}
{code}
```

错误信息：
{error}

请提供详细的错误分析，包括：
1. 错误的类型
2. 错误的原因
3. 可能的修复方案
"""

        try:
            response = await self._call_llm(
                system_prompt=system_prompt,
                user_message="分析代码错误"
            )
            return response

        except Exception as e:
            logger.error(f"错误分析失败: {e}")
            return f"错误分析失败: {str(e)}"

    async def optimize_code(self, code: str, language: str = 'python') -> str:
        """
        优化代码性能

        Args:
            code: 原始代码
            language: 代码语言

        Returns:
            str: 优化后的代码
        """
        system_prompt = f"""
你是一个专业的{language}性能优化专家。请优化以下代码的性能：

原代码：
```{language}
{code}
```

要求：
1. 保持原有功能不变
2. 提高代码执行效率
3. 改善代码可读性和可维护性
4. 遵循该语言的最佳实践
5. 只返回优化后的代码
"""

        try:
            response = await self._call_llm(
                system_prompt=system_prompt,
                user_message="优化代码性能"
            )

            optimized_code = self._extract_code_from_response(response)
            return optimized_code

        except Exception as e:
            logger.error(f"代码优化失败: {e}")
            return code

    async def generate_tests(self, code: str, language: str = 'python', framework: str = 'unittest') -> str:
        """
        为代码生成单元测试

        Args:
            code: 要测试的代码
            language: 代码语言
            framework: 测试框架

        Returns:
            str: 生成的测试代码
        """
        system_prompt = f"""
你是一个专业的测试工程师。请为以下{language}代码生成完整的单元测试。

代码：
```{language}
{code}
```

要求：
1. 使用{framework}框架
2. 覆盖各种边界情况
3. 包含正常情况和异常情况的测试
4. 测试应该具有可读性和可维护性
5. 只返回测试代码
"""

        try:
            response = await self._call_llm(
                system_prompt=system_prompt,
                user_message="生成单元测试"
            )

            test_code = self._extract_code_from_response(response)
            return test_code

        except Exception as e:
            logger.error(f"测试生成失败: {e}")
            return f"# 测试生成失败: {str(e)}"

    async def explain_code(self, code: str, language: str = 'python') -> str:
        """
        解释代码的功能

        Args:
            code: 要解释的代码
            language: 代码语言

        Returns:
            str: 代码解释
        """
        system_prompt = f"""
请详细解释以下{language}代码的功能和实现原理：

```{language}
{code}
```

请提供：
1. 代码的整体功能
2. 关键算法和数据结构
3. 代码的工作流程
4. 可能的改进建议
"""

        try:
            response = await self._call_llm(
                system_prompt=system_prompt,
                user_message="解释代码"
            )
            return response

        except Exception as e:
            logger.error(f"代码解释失败: {e}")
            return f"代码解释失败: {str(e)}"

    def _extract_code_from_response(self, response: str) -> str:
        """
        从模型响应中提取代码块

        Args:
            response: LLM的响应文本

        Returns:
            str: 提取的代码
        """
        # 匹配代码块（支持多种语言标记）
        code_pattern = r'```(?:\w+)?\n([\s\S]*?)\n```'
        matches = re.findall(code_pattern, response)

        if matches:
            return matches[0].strip()

        # 如果没有代码块标记，检查是否有单行代码标记
        if '```' in response and not matches:
            # 可能是格式不完整的代码块，尝试提取整个内容
            content = re.sub(r'```\w*\n?', '', response).strip()
            if content:
                return content

        # 如果没有代码块标记，返回整个响应
        return response.strip()

    async def _call_llm(self, system_prompt: str, user_message: str) -> str:
        """
        调用大语言模型

        Args:
            system_prompt: 系统提示
            user_message: 用户消息

        Returns:
            str: 模型响应
        """
        if hasattr(self.llm, 'chat_completion'):
            # 支持OpenAI风格的API
            response = await self.llm.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            return response
        elif hasattr(self.llm, 'generate'):
            # 简单的generate方法
            response = await self.llm.generate(f"{system_prompt}\n\n{user_message}")
            return response
        else:
            raise ValueError("不支持的LLM客户端类型")
