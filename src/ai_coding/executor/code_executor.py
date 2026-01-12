# -*- coding: utf-8 -*-
"""
AI Coding Assistant - 代码执行引擎
提供安全的沙箱环境来执行代码
"""

import tempfile
import os
import shutil
from typing import Dict, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)


class CodeExecutor:
    """安全的代码执行引擎"""

    def __init__(self, timeout: int = 30, memory_limit: str = "100m", cpu_quota: int = 50000):
        """
        初始化代码执行器

        Args:
            timeout: 执行超时时间（秒）
            memory_limit: 内存限制
            cpu_quota: CPU配额
        """
        self.timeout = timeout
        self.memory_limit = memory_limit
        self.cpu_period = 100000
        self.cpu_quota = cpu_quota
        self.use_docker = self._check_docker_available()

    def _check_docker_available(self) -> bool:
        """
        检查Docker是否可用

        Returns:
            bool: Docker是否可用
        """
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

    async def execute_python(self, code: str, input_data: str = "") -> Dict:
        """
        安全执行Python代码

        Args:
            code: 要执行的Python代码
            input_data: 标准输入数据

        Returns:
            Dict: 执行结果，包含success, output, error, exit_code等字段
        """
        if self.use_docker:
            return await self._execute_python_in_docker(code, input_data)
        else:
            return await self._execute_python_locally(code, input_data)

    async def _execute_python_in_docker(self, code: str, input_data: str = "") -> Dict:
        """
        在Docker容器中执行Python代码

        Args:
            code: 要执行的Python代码
            input_data: 标准输入数据

        Returns:
            Dict: 执行结果
        """
        try:
            import docker
        except ImportError:
            logger.error("Docker模块未安装")
            return {'success': False, 'error': 'Docker未安装'}

        client = docker.from_env()

        with tempfile.TemporaryDirectory() as tmpdir:
            # 写入代码文件
            code_path = os.path.join(tmpdir, "code.py")
            with open(code_path, "w", encoding='utf-8') as f:
                f.write(code)

            # 写入输入数据
            input_path = os.path.join(tmpdir, "input.txt")
            with open(input_path, "w", encoding='utf-8') as f:
                f.write(input_data)

            # Docker容器配置
            container_config = {
                'image': 'python:3.9-slim',
                'volumes': {tmpdir: {'bind': '/workspace', 'mode': 'rw'}},
                'working_dir': '/workspace',
                'mem_limit': self.memory_limit,
                'cpu_period': self.cpu_period,
                'cpu_quota': self.cpu_quota,
                'network_disabled': True,  # 禁用网络
                'read_only': False,  # 需要写入权限
                'detach': False,
                'remove': True,
            }

            try:
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: client.containers.run(
                        command=f"timeout {self.timeout} python code.py < input.txt",
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
                    'exit_code': 0
                }

            except Exception as e:
                error_msg = str(e)
                if "exit code" in error_msg.lower():
                    exit_code = int(error_msg.split("exit code ")[-1].split(")")[0])
                    return {
                        'success': False,
                        'output': '',
                        'error': error_msg,
                        'exit_code': exit_code
                    }
                return {'success': False, 'error': error_msg, 'exit_code': -1}

    async def _execute_python_locally(self, code: str, input_data: str = "") -> Dict:
        """
        在本地执行Python代码（不使用Docker）

        Args:
            code: 要执行的Python代码
            input_data: 标准输入数据

        Returns:
            Dict: 执行结果
        """
        import sys
        import subprocess

        with tempfile.TemporaryDirectory() as tmpdir:
            code_path = os.path.join(tmpdir, "code.py")
            with open(code_path, "w", encoding='utf-8') as f:
                f.write(code)

            input_path = os.path.join(tmpdir, "input.txt")
            with open(input_path, "w", encoding='utf-8') as f:
                f.write(input_data)

            try:
                process = await asyncio.create_subprocess_exec(
                    sys.executable,
                    code_path,
                    stdin=open(input_path, 'r', encoding='utf-8'),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=tmpdir
                )

                # 设置超时
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
                        'exit_code': -1
                    }

                output = stdout.decode('utf-8', errors='replace')
                error = stderr.decode('utf-8', errors='replace')

                return {
                    'success': process.returncode == 0,
                    'output': output,
                    'error': error,
                    'exit_code': process.returncode
                }

            except Exception as e:
                logger.error(f"本地执行失败: {e}")
                return {'success': False, 'error': str(e), 'exit_code': -1}
