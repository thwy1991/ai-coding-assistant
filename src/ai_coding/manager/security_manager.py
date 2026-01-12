# -*- coding: utf-8 -*-
"""
AI Coding Assistant - 安全管理器
提供代码安全检查和风险防护功能
"""

import re
import ast
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class SecurityManager:
    """安全管理器，负责代码安全检查和风险防护"""

    # 危险操作黑名单
    BLACKLISTED_COMMANDS = [
        'rm -rf', 'format', 'dd', 'mkfs',
        'shutdown', 'reboot', 'halt',
        'del /s', 'rmdir /s', 'format c:',
    ]

    # 危险导入和函数
    BLACKLISTED_IMPORTS = [
        'os.system', 'subprocess.run', 'eval',
        'exec', '__import__', 'compile',
        'pickle.loads', 'marshal.loads',
    ]

    # 危险模块
    BLACKLISTED_MODULES = [
        'subprocess', 'os', 'sys', 'socket',
        'ftplib', 'urllib', 'http',
    ]

    # Python危险关键字
    PYTHON_DANGEROUS_KEYWORDS = [
        '__import__', 'eval', 'exec', 'compile',
        'open(',
    ]

    def __init__(self, enable_sandbox: bool = True, max_code_length: int = 10000):
        """
        初始化安全管理器

        Args:
            enable_sandbox: 是否启用沙箱模式
            max_code_length: 最大代码长度
        """
        self.enable_sandbox = enable_sandbox
        self.max_code_length = max_code_length

    def sanitize_code(self, code: str, language: str = 'python') -> Dict:
        """
        代码安全检查

        Args:
            code: 要检查的代码
            language: 代码语言

        Returns:
            Dict: 检查结果，包含safe, issues, sanitized_code等
        """
        issues = []

        # 1. 检查代码长度
        if len(code) > self.max_code_length:
            issues.append(f"代码过长 ({len(code)} > {self.max_code_length})")

        # 2. 语言特定的检查
        if language.lower() == 'python':
            issues.extend(self._check_python_code(code))
        elif language.lower() in ['javascript', 'js']:
            issues.extend(self._check_javascript_code(code))
        elif language.lower() == 'bash':
            issues.extend(self._check_bash_code(code))

        # 3. 检查危险命令
        for cmd in self.BLACKLISTED_COMMANDS:
            if cmd.lower() in code.lower():
                issues.append(f"检测到危险命令: {cmd}")

        # 4. 检查递归调用
        if self._detect_infinite_recursion(code):
            issues.append("可能包含无限递归")

        return {
            'safe': len(issues) == 0,
            'issues': issues,
            'sanitized_code': self._remove_dangerous_code(code, language) if issues else code,
            'warnings': self._get_warnings(code, language)
        }

    def _check_python_code(self, code: str) -> List[str]:
        """
        检查Python代码

        Args:
            code: Python代码

        Returns:
            List[str]: 发现的问题列表
        """
        issues = []

        # 检查危险导入
        for imp in self.BLACKLISTED_IMPORTS:
            if imp in code:
                issues.append(f"检测到危险导入/函数: {imp}")

        # 尝试解析AST
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                # 检查import语句
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in self.BLACKLISTED_MODULES:
                            issues.append(f"检测到危险模块导入: {alias.name}")

                # 检查from import
                if isinstance(node, ast.ImportFrom):
                    if node.module and node.module in self.BLACKLISTED_MODULES:
                        issues.append(f"检测到危险模块导入: {node.module}")

                # 检查函数调用
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                        if func_name in ['eval', 'exec', 'compile', '__import__']:
                            issues.append(f"检测到危险函数调用: {func_name}")

        except SyntaxError as e:
            issues.append(f"语法错误: {e}")

        return issues

    def _check_javascript_code(self, code: str) -> List[str]:
        """
        检查JavaScript代码

        Args:
            code: JavaScript代码

        Returns:
            List[str]: 发现的问题列表
        """
        issues = []

        # 检查eval和Function
        if 'eval(' in code:
            issues.append("检测到eval函数")

        if 'new Function(' in code:
            issues.append("检测到Function构造函数")

        # 检查document.write
        if 'document.write' in code:
            issues.append("检测到document.write（可能存在XSS风险）")

        return issues

    def _check_bash_code(self, code: str) -> List[str]:
        """
        检查Bash代码

        Args:
            code: Bash代码

        Returns:
            List[str]: 发现的问题列表
        """
        issues = []

        # 检查危险命令
        dangerous_patterns = [
            r'rm\s+-rf\s+/',
            r'dd\s+if=',
            r'mkfs.',
            r':\(\)\{\s*:\|:&\s*\}\;',
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, code):
                issues.append(f"检测到危险Bash命令: {pattern}")

        return issues

    def _detect_infinite_recursion(self, code: str) -> bool:
        """
        检测可能的无限递归

        Args:
            code: 代码

        Returns:
            bool: 是否可能包含无限递归
        """
        # 简单检测：查找没有终止条件的递归函数
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 检查函数体内是否有对自身的调用
                    for subnode in ast.walk(node):
                        if isinstance(subnode, ast.Call):
                            if isinstance(subnode.func, ast.Name):
                                if subnode.func.id == node.name:
                                    # 找到递归调用，检查是否有终止条件
                                    if not self._has_termination_condition(node):
                                        return True
        except Exception:
            pass

        return False

    def _has_termination_condition(self, func_node) -> bool:
        """
        检查函数是否有终止条件

        Args:
            func_node: AST函数节点

        Returns:
            bool: 是否有终止条件
        """
        # 检查是否有if、while等控制流
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While)):
                return True

        return False

    def _remove_dangerous_code(self, code: str, language: str) -> str:
        """
        移除危险代码

        Args:
            code: 原始代码
            language: 代码语言

        Returns:
            str: 清理后的代码
        """
        sanitized = code

        # 移除危险导入
        for imp in self.BLACKLISTED_IMPORTS:
            sanitized = sanitized.replace(imp, f"# REMOVED: {imp}")

        return sanitized

    def _get_warnings(self, code: str, language: str) -> List[str]:
        """
        获取警告信息（非致命问题）

        Args:
            code: 代码
            language: 代码语言

        Returns:
            List[str]: 警告列表
        """
        warnings = []

        # 检查是否有密码、密钥等敏感信息
        sensitive_patterns = [
            r'password\s*=\s*[\'"][^\'"]+[\'"]',
            r'api[_-]?key\s*=\s*[\'"][^\'"]+[\'"]',
            r'secret\s*=\s*[\'"][^\'"]+[\'"]',
        ]

        for pattern in sensitive_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                warnings.append("代码中可能包含敏感信息（密码、密钥等）")

        # 检查是否有硬编码的IP地址
        if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', code):
            warnings.append("代码中包含硬编码的IP地址")

        return warnings

    def is_safe_to_execute(self, code: str, language: str = 'python') -> bool:
        """
        检查代码是否安全可以执行

        Args:
            code: 代码
            language: 语言

        Returns:
            bool: 是否安全
        """
        result = self.sanitize_code(code, language)
        return result['safe']

    def get_security_summary(self) -> Dict:
        """
        获取安全管理器配置摘要

        Returns:
            Dict: 配置摘要
        """
        return {
            'enable_sandbox': self.enable_sandbox,
            'max_code_length': self.max_code_length,
            'blacklisted_commands': len(self.BLACKLISTED_COMMANDS),
            'blacklisted_imports': len(self.BLACKLISTED_IMPORTS)
        }

    def set_max_code_length(self, length: int):
        """
        设置最大代码长度

        Args:
            length: 最大长度
        """
        self.max_code_length = length

    def enable_sandbox_mode(self):
        """启用沙箱模式"""
        self.enable_sandbox = True

    def disable_sandbox_mode(self):
        """禁用沙箱模式"""
        self.enable_sandbox = False
