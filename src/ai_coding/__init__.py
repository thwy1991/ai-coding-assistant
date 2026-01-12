# -*- coding: utf-8 -*-
"""
AI Coding Assistant - AI编程助手
类似Claude Code的代码执行能力，支持多语言代码生成、执行和调试
"""

from .executor.code_executor import CodeExecutor
from .executor.multi_language_executor import MultiLanguageExecutor
from .generator.ai_code_generator import AICodeGenerator
from .debugger.interactive_debugger import InteractiveDebugger
from .manager.project_manager import ProjectManager
from .manager.security_manager import SecurityManager
from .workflow import AICodingWorkflow
from .llm_clients import OpenAIClient, MockLLMClient, create_llm_client

__version__ = '0.1.0'
__all__ = [
    'CodeExecutor',
    'MultiLanguageExecutor',
    'AICodeGenerator',
    'InteractiveDebugger',
    'ProjectManager',
    'SecurityManager',
    'AICodingWorkflow',
    'OpenAIClient',
    'MockLLMClient',
    'create_llm_client',
]
