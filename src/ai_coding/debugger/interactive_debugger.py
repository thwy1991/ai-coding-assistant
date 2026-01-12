# -*- coding: utf-8 -*-
"""
AI Coding Assistant - 交互式调试器
提供自动调试和代码修复功能
"""

import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class InteractiveDebugger:
    """交互式调试器，支持自动调试和代码修复"""

    def __init__(self, llm_api, executor, code_generator):
        """
        初始化调试器

        Args:
            llm_api: 大语言模型API
            executor: 代码执行器
            code_generator: 代码生成器
        """
        self.llm = llm_api
        self.executor = executor
        self.code_generator = code_generator
        self.max_retries = 3

    async def debug_and_fix(self, original_code: str, error: str, language: str = 'python') -> Dict:
        """
        自动调试和修复代码

        Args:
            original_code: 原始代码
            error: 错误信息
            language: 代码语言

        Returns:
            Dict: 修复结果，包含success, fixed_code, attempts, explanation等
        """
        current_code = original_code
        current_error = error

        for attempt in range(self.max_retries):
            logger.info(f"尝试修复代码（第{attempt + 1}次）...")

            # 1. 分析错误
            analysis = await self.analyze_error(current_code, current_error, language)

            # 2. 生成修复建议
            fixed_code = await self.code_generator.fix_code(current_code, current_error, language)

            # 3. 测试修复
            test_result = await self._test_code(fixed_code, language)

            if test_result['success']:
                logger.info(f"代码修复成功！（共尝试{attempt + 1}次）")
                return {
                    'success': True,
                    'fixed_code': fixed_code,
                    'attempts': attempt + 1,
                    'explanation': analysis,
                    'execution_result': test_result
                }
            else:
                # 更新当前代码和错误，准备下一次尝试
                current_code = fixed_code
                current_error = test_result.get('error', '未知错误')
                logger.warning(f"第{attempt + 1}次修复失败，错误: {current_error}")

        logger.error(f"无法修复代码，已尝试{self.max_retries}次")
        return {
            'success': False,
            'error': f'无法修复代码，已尝试{self.max_retries}次',
            'attempts': self.max_retries,
            'original_code': original_code,
            'last_error': current_error
        }

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
        return await self.code_generator.analyze_error(code, error, language)

    async def _test_code(self, code: str, language: str) -> Dict:
        """
        测试代码是否能正常运行

        Args:
            code: 要测试的代码
            language: 代码语言

        Returns:
            Dict: 测试结果
        """
        try:
            if language == 'python':
                result = await self.executor.execute_python(code)
            else:
                result = await self.executor.execute(language, code)
            return result
        except Exception as e:
            logger.error(f"测试代码时出错: {e}")
            return {'success': False, 'error': str(e), 'exit_code': -1}

    async def debug_with_step_by_step(self, code: str, language: str = 'python',
                                      input_data: str = "") -> Dict:
        """
        逐步调试代码

        Args:
            code: 要调试的代码
            language: 代码语言
            input_data: 输入数据

        Returns:
            Dict: 调试结果
        """
        # 先执行代码
        result = await self._test_code(code, language)

        if result['success']:
            return {
                'success': True,
                'message': '代码执行成功，无需调试',
                'execution_result': result
            }

        # 如果失败，尝试自动修复
        return await self.debug_and_fix(code, result['error'], language)

    async def suggest_fixes(self, code: str, error: str, language: str = 'python') -> List[str]:
        """
        生成修复建议（不自动修复，只提供建议）

        Args:
            code: 原始代码
            error: 错误信息
            language: 代码语言

        Returns:
            List[str]: 修复建议列表
        """
        system_prompt = f"""
你是一个专业的{language}调试专家。请分析以下代码的错误并提供多个修复建议。

代码：
```{language}
{code}
```

错误信息：
{error}

请提供3-5个不同的修复建议，每个建议应该：
1. 说明问题所在
2. 给出具体的修复方案
3. 提供修复后的代码片段

请以JSON格式返回，格式如下：
{{
    "suggestions": [
        {{
            "issue": "问题描述",
            "solution": "解决方案说明",
            "code": "修复后的代码片段"
        }}
    ]
}}
"""

        try:
            if hasattr(self.llm, 'chat_completion'):
                response = await self.llm.chat_completion(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": "提供修复建议"}
                    ]
                )
            else:
                response = await self.llm.generate(system_prompt)

            # 尝试解析JSON响应
            import json
            result = json.loads(response)
            return result.get('suggestions', [])

        except Exception as e:
            logger.error(f"生成修复建议失败: {e}")
            return [{"issue": "无法生成建议", "solution": str(e), "code": ""}]

    async def validate_code(self, code: str, language: str = 'python') -> Dict:
        """
        验证代码的正确性

        Args:
            code: 要验证的代码
            language: 代码语言

        Returns:
            Dict: 验证结果
        """
        system_prompt = f"""
请验证以下{language}代码的正确性和安全性：

```{language}
{code}
```

请检查：
1. 语法是否正确
2. 是否有逻辑错误
3. 是否存在安全隐患
4. 是否符合最佳实践
5. 是否有性能问题

请以JSON格式返回，格式如下：
{{
    "is_valid": true/false,
    "issues": ["问题1", "问题2"],
    "warnings": ["警告1", "警告2"],
    "suggestions": ["建议1", "建议2"]
}}
"""

        try:
            if hasattr(self.llm, 'chat_completion'):
                response = await self.llm.chat_completion(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": "验证代码"}
                    ]
                )
            else:
                response = await self.llm.generate(system_prompt)

            # 尝试解析JSON响应
            import json
            result = json.loads(response)
            return result

        except Exception as e:
            logger.error(f"代码验证失败: {e}")
            return {
                "is_valid": False,
                "issues": [f"验证失败: {str(e)}"],
                "warnings": [],
                "suggestions": []
            }

    def set_max_retries(self, max_retries: int):
        """
        设置最大重试次数

        Args:
            max_retries: 最大重试次数
        """
        self.max_retries = max_retries
