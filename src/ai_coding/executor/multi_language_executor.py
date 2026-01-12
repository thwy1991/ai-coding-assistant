# -*- coding: utf-8 -*-
"""
AI Coding Assistant - 多语言执行器
支持Python、JavaScript、Java、Go、Rust、Bash等多种语言
"""

import tempfile
import os
import sys
import asyncio
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class MultiLanguageExecutor:
    """多语言代码执行器"""

    SUPPORTED_LANGUAGES = {
        'python': {
            'image': 'python:3.9-slim',
            'command': 'python code.py < input.txt',
            'file_ext': '.py',
            'use_docker': True
        },
        'javascript': {
            'image': 'node:16-slim',
            'command': 'node code.js < input.txt',
            'file_ext': '.js',
            'use_docker': True
        },
        'java': {
            'image': 'openjdk:11-slim',
            'command': 'javac code.java && java Main < input.txt',
            'file_ext': '.java',
            'use_docker': True
        },
        'go': {
            'image': 'golang:1.19-alpine',
            'command': 'go run code.go < input.txt',
            'file_ext': '.go',
            'use_docker': True
        },
        'rust': {
            'image': 'rust:slim',
            'command': 'rustc code.rs -o app && ./app < input.txt',
            'file_ext': '.rs',
            'use_docker': True
        },
        'bash': {
            'image': 'alpine',
            'command': 'sh code.sh < input.txt',
            'file_ext': '.sh',
            'use_docker': True
        },
        'c': {
            'image': 'gcc:latest',
            'command': 'gcc code.c -o app && ./app < input.txt',
            'file_ext': '.c',
            'use_docker': True
        },
        'cpp': {
            'image': 'gcc:latest',
            'command': 'g++ code.cpp -o app && ./app < input.txt',
            'file_ext': '.cpp',
            'use_docker': True
        }
    }

    def __init__(self, timeout: int = 30, memory_limit: str = "100m", execution_mode: str = "auto"):
        """
        初始化多语言执行器

        Args:
            timeout: 执行超时时间（秒）
            memory_limit: 内存限制
            execution_mode: 执行模式 (auto, docker, local, daytona)
        """
        self.timeout = timeout
        self.memory_limit = memory_limit
        self.execution_mode = execution_mode.lower()
        self.use_docker = self._check_docker_available()

        # Daytona执行器
        self.daytona_executor = None
        if self.execution_mode == "daytona":
            from .daytona_executor import DaytonaExecutor
            self.daytona_executor = DaytonaExecutor()

    def _check_docker_available(self) -> bool:
        """检查Docker是否可用"""
        try:
            import docker
            client = docker.from_env()
            client.ping()
            return True
        except ImportError:
            logger.warning("Docker Python包未安装，将使用本地执行")
            return False
        except Exception as e:
            error_msg = str(e)
            if "CreateFile" in error_msg or "系统找不到指定的文件" in error_msg:
                logger.warning("Docker服务未运行，将使用本地执行")
            else:
                logger.warning(f"Docker不可用: {e}，将使用本地执行")
            return False

    async def execute(self, language: str, code: str, stdin: str = "") -> Dict:
        """
        执行指定语言的代码

        Args:
            language: 编程语言
            code: 要执行的代码
            stdin: 标准输入

        Returns:
            Dict: 执行结果
        """
        language = language.lower()

        if language not in self.SUPPORTED_LANGUAGES:
            return {
                'success': False,
                'error': f"不支持的语言: {language}. 支持的语言: {list(self.SUPPORTED_LANGUAGES.keys())}",
                'exit_code': -1
            }

        config = self.SUPPORTED_LANGUAGES[language]

        # 根据执行模式选择执行方式
        if self.execution_mode == "daytona":
            if not self.daytona_executor:
                return {
                    'success': False,
                    'error': 'Daytona模式需要API密钥配置',
                    'exit_code': -1
                }
            result = await self.daytona_executor.execute_code(code, language)
            result['language'] = language
            return result

        elif self.execution_mode == "docker":
            if not self.use_docker:
                return {
                    'success': False,
                    'error': 'Docker不可用，无法执行',
                    'exit_code': -1
                }
            return await self._execute_in_docker(language, code, stdin, config)

        elif self.execution_mode == "local":
            return await self._execute_locally(language, code, stdin, config)

        else:  # auto模式
            # 如果需要Docker但不可用，尝试本地执行
            if config['use_docker'] and not self.use_docker:
                logger.info(f"Docker不可用，尝试本地执行{language}代码")
                return await self._execute_locally(language, code, stdin, config)

            if self.use_docker and config['use_docker']:
                return await self._execute_in_docker(language, code, stdin, config)
            else:
                return await self._execute_locally(language, code, stdin, config)

    async def _execute_in_docker(self, language: str, code: str, stdin: str, config: Dict) -> Dict:
        """在Docker容器中执行代码"""
        try:
            import docker
        except ImportError:
            return {'success': False, 'error': 'Docker未安装', 'exit_code': -1}

        client = docker.from_env()

        with tempfile.TemporaryDirectory() as tmpdir:
            # 写入代码文件
            file_ext = config['file_ext']
            code_filename = f"code{file_ext}"
            code_path = os.path.join(tmpdir, code_filename)

            with open(code_path, "w", encoding='utf-8') as f:
                f.write(code)

            # 写入输入数据
            input_path = os.path.join(tmpdir, "input.txt")
            with open(input_path, "w", encoding='utf-8') as f:
                f.write(stdin)

            # Docker容器配置
            container_config = {
                'image': config['image'],
                'volumes': {tmpdir: {'bind': '/workspace', 'mode': 'rw'}},
                'working_dir': '/workspace',
                'mem_limit': self.memory_limit,
                'network_disabled': True,
                'detach': False,
                'remove': True,
            }

            try:
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: client.containers.run(
                        command=f"timeout {self.timeout} sh -c '{config['command']}'",
                        **container_config,
                        stdout=True,
                        stderr=True
                    )
                )

                output = result.decode('utf-8', errors='replace') if result else ''

                return {
                    'success': True,
                    'output': output,
                    'error': '',
                    'exit_code': 0,
                    'language': language
                }

            except Exception as e:
                error_msg = str(e)
                return {
                    'success': False,
                    'output': '',
                    'error': error_msg,
                    'exit_code': -1,
                    'language': language
                }

    async def _execute_locally(self, language: str, code: str, stdin: str, config: Dict) -> Dict:
        """在本地执行代码（不使用Docker）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_ext = config['file_ext']
            code_filename = f"code{file_ext}"
            code_path = os.path.join(tmpdir, code_filename)

            with open(code_path, "w", encoding='utf-8') as f:
                f.write(code)

            input_path = os.path.join(tmpdir, "input.txt")
            with open(input_path, "w", encoding='utf-8') as f:
                f.write(stdin)

            try:
                # 根据语言类型选择执行器
                if language == 'python':
                    executor = sys.executable
                    args = [code_path]
                elif language == 'javascript':
                    executor = 'node'
                    args = [code_path]
                elif language == 'bash':
                    executor = 'sh'
                    args = [code_path]
                elif language == 'c':
                    # 需要先编译
                    app_path = os.path.join(tmpdir, "app")
                    compile_process = await asyncio.create_subprocess_exec(
                        'gcc', code_path, '-o', app_path,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    _, compile_err = await compile_process.communicate()
                    if compile_process.returncode != 0:
                        return {
                            'success': False,
                            'error': f'编译失败: {compile_err.decode("utf-8", errors="replace")}',
                            'exit_code': compile_process.returncode,
                            'language': language
                        }
                    executor = app_path
                    args = []
                else:
                    return {
                        'success': False,
                        'error': f'本地模式不支持该语言: {language}',
                        'exit_code': -1,
                        'language': language
                    }

                process = await asyncio.create_subprocess_exec(
                    executor, *args,
                    stdin=open(input_path, 'r', encoding='utf-8'),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=tmpdir
                )

                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=self.timeout
                    )
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
                    return {
                        'success': False,
                        'error': f'执行超时（{self.timeout}秒）',
                        'exit_code': -1,
                        'language': language
                    }

                output = stdout.decode('utf-8', errors='replace')
                error = stderr.decode('utf-8', errors='replace')

                return {
                    'success': process.returncode == 0,
                    'output': output,
                    'error': error,
                    'exit_code': process.returncode,
                    'language': language
                }

            except Exception as e:
                logger.error(f"本地执行失败: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'exit_code': -1,
                    'language': language
                }

    def get_supported_languages(self) -> list:
        """获取支持的语言列表"""
        return list(self.SUPPORTED_LANGUAGES.keys())

    def is_supported(self, language: str) -> bool:
        """检查是否支持该语言"""
        return language.lower() in self.SUPPORTED_LANGUAGES
