# -*- coding: utf-8 -*-
"""
AI Coding Assistant - 主工作流
整合所有模块，提供完整的AI编程助手功能
"""

import json
import logging
from typing import Dict, Optional, List

from .executor.multi_language_executor import MultiLanguageExecutor
from .generator.ai_code_generator import AICodeGenerator
from .debugger.interactive_debugger import InteractiveDebugger
from .manager.project_manager import ProjectManager
from .manager.security_manager import SecurityManager

logger = logging.getLogger(__name__)


class AICodingWorkflow:
    """AI编程助手主工作流"""

    def __init__(self, llm_client, config: Optional[Dict] = None):
        """
        初始化工作流

        Args:
            llm_client: 大语言模型客户端
            config: 配置字典
        """
        self.llm = llm_client

        # 解析配置
        config = config or {}
        workspace_path = config.get('workspace_path', './workspace')
        sandbox_config = config.get('sandbox', {})
        security_config = config.get('security', {})

        # 初始化各模块
        self.executor = MultiLanguageExecutor(
            timeout=sandbox_config.get('timeout', 30),
            memory_limit=sandbox_config.get('memory_limit', '100m'),
            execution_mode=sandbox_config.get('execution_mode', 'auto')
        )

        self.code_generator = AICodeGenerator(self.llm)

        self.debugger = InteractiveDebugger(
            self.llm,
            self.executor,
            self.code_generator
        )

        self.project_manager = ProjectManager(base_path=workspace_path)

        self.security_manager = SecurityManager(
            enable_sandbox=security_config.get('enable_sandbox', True),
            max_code_length=security_config.get('max_code_length', 10000)
        )

        # 对话历史
        self.conversation_history: List[Dict] = []

        logger.info("AI编程助手初始化完成")

    async def handle_request(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """
        处理用户请求的完整流程

        Args:
            user_input: 用户输入
            context: 上下文信息

        Returns:
            Dict: 处理结果
        """
        context = context or {}

        # 步骤1：理解用户意图
        intent = await self._analyze_intent(user_input)
        logger.info(f"用户意图: {intent}")

        response = {}

        # 步骤2：根据意图执行不同操作
        if intent.get('action') == 'create_file':
            # 创建文件
            response = await self._handle_create_file(user_input, intent, context)
        elif intent.get('action') == 'execute_code':
            # 执行代码
            response = await self._handle_execute_code(user_input, intent, context)
        elif intent.get('action') == 'debug':
            # 调试代码
            response = await self._handle_debug(user_input, intent, context)
        elif intent.get('action') == 'explain':
            # 解释代码
            response = await self._handle_explain(user_input, intent, context)
        else:
            # 默认：生成代码
            response = await self._handle_generate(user_input, intent, context)

        # 步骤3：更新对话历史
        self._update_conversation_history(user_input, response)

        return response

    async def _analyze_intent(self, user_input: str) -> Dict:
        """
        使用LLM分析用户意图

        Args:
            user_input: 用户输入

        Returns:
            Dict: 意图信息
        """
        intent_prompt = f"""
分析用户请求的意图，返回JSON格式：

用户输入：{user_input}

请返回JSON格式（不要包含其他文字）：
{{
    "action": "create_file|execute_code|debug|explain|generate",
    "language": "python|javascript|java|go|rust|bash|cpp",
    "filename": "可选，文件名",
    "should_execute": true|false,
    "confidence": 0.0-1.0
}}
"""

        try:
            if hasattr(self.llm, 'chat_completion'):
                response = await self.llm.chat_completion(
                    messages=[
                        {"role": "system", "content": "你是一个意图识别助手，只返回JSON格式结果。"},
                        {"role": "user", "content": intent_prompt}
                    ]
                )
            else:
                response = await self.llm.generate(intent_prompt)

            # 尝试解析JSON
            intent = json.loads(self._extract_json(response))
            return intent

        except Exception as e:
            logger.warning(f"意图分析失败: {e}，使用默认意图")
            return {
                'action': 'generate',
                'language': 'python',
                'should_execute': False,
                'confidence': 0.5
            }

    def _extract_json(self, text: str) -> str:
        """从文本中提取JSON"""
        import re
        # 查找JSON对象
        match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
        if match:
            return match.group(0)
        return text

    async def _handle_create_file(self, user_input: str, intent: Dict, context: Dict) -> Dict:
        """处理创建文件请求"""
        # 生成代码
        code = await self.code_generator.generate_code(
            user_input,
            intent.get('language', 'python')
        )

        # 安全检查
        security_check = self.security_manager.sanitize_code(code, intent.get('language', 'python'))
        if not security_check['safe']:
            logger.warning(f"代码安全检查未通过: {security_check['issues']}")

        # 创建文件
        filename = intent.get('filename', f'output.{intent.get("language", "python")}')
        file_path = self.project_manager.create_file(filename, code)

        return {
            'action': 'create_file',
            'success': True,
            'file_path': file_path,
            'code': code,
            'security_issues': security_check['issues']
        }

    async def _handle_execute_code(self, user_input: str, intent: Dict, context: Dict) -> Dict:
        """处理执行代码请求"""
        # 生成代码
        code = await self.code_generator.generate_code(
            user_input,
            intent.get('language', 'python')
        )

        # 安全检查
        security_check = self.security_manager.sanitize_code(code, intent.get('language', 'python'))
        if not security_check['safe']:
            return {
                'action': 'execute_code',
                'success': False,
                'error': f'代码安全检查未通过: {security_check["issues"]}',
                'code': code
            }

        # 执行代码
        result = await self.executor.execute(
            language=intent.get('language', 'python'),
            code=code,
            stdin=intent.get('stdin', '')
        )

        if result['success']:
            response = {
                'action': 'execute_code',
                'success': True,
                'code': code,
                'output': result['output'],
                'exit_code': result['exit_code']
            }
        else:
            # 自动调试
            debug_result = await self.debugger.debug_and_fix(
                code, result['error'], intent.get('language', 'python')
            )

            response = {
                'action': 'execute_code',
                'success': debug_result['success'],
                'code': debug_result.get('fixed_code', code),
                'output': debug_result.get('execution_result', {}).get('output', ''),
                'error': result['error'],
                'fixed': debug_result['success'],
                'attempts': debug_result.get('attempts', 0)
            }

        return response

    async def _handle_debug(self, user_input: str, intent: Dict, context: Dict) -> Dict:
        """处理调试请求"""
        # 从上下文中获取代码
        code = context.get('code', '')

        if not code:
            return {
                'action': 'debug',
                'success': False,
                'error': '没有提供要调试的代码'
            }

        # 执行代码以获取错误
        result = await self.executor.execute(
            language=intent.get('language', 'python'),
            code=code
        )

        if result['success']:
            return {
                'action': 'debug',
                'success': True,
                'message': '代码执行成功，无需调试'
            }

        # 调试代码
        debug_result = await self.debugger.debug_and_fix(
            code, result['error'], intent.get('language', 'python')
        )

        return debug_result

    async def _handle_explain(self, user_input: str, intent: Dict, context: Dict) -> Dict:
        """处理代码解释请求"""
        code = context.get('code', '')

        if not code:
            return {
                'action': 'explain',
                'success': False,
                'error': '没有提供要解释的代码'
            }

        explanation = await self.code_generator.explain_code(
            code,
            intent.get('language', 'python')
        )

        return {
            'action': 'explain',
            'success': True,
            'explanation': explanation
        }

    async def _handle_generate(self, user_input: str, intent: Dict, context: Dict) -> Dict:
        """处理代码生成请求"""
        code = await self.code_generator.generate_code(
            user_input,
            intent.get('language', 'python')
        )

        return {
            'action': 'generate',
            'success': True,
            'code': code,
            'language': intent.get('language', 'python')
        }

    def _update_conversation_history(self, user_input: str, response: Dict):
        """更新对话历史"""
        self.conversation_history.append({
            'user': user_input,
            'assistant': response
        })

        # 限制历史记录数量
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]

    def get_conversation_history(self) -> List[Dict]:
        """获取对话历史"""
        return self.conversation_history

    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []

    def get_project_context(self) -> Dict:
        """获取项目上下文"""
        return self.project_manager.get_project_context()
