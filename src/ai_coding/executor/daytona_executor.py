# -*- coding: utf-8 -*-
"""
AI Coding Assistant - Daytona API客户端
使用Daytona API在云端沙箱中执行代码
"""

import os
import logging
from typing import Dict, Optional
import aiohttp
import asyncio

logger = logging.getLogger(__name__)


class DaytonaExecutor:
    """Daytona API执行器 - 在云端沙箱中执行代码"""

    def __init__(self, api_key: Optional[str] = None, workspace_id: Optional[str] = None):
        """
        初始化Daytona执行器

        Args:
            api_key: Daytona API密钥
            workspace_id: Daytona工作区ID（可选，如果不提供会自动创建）
        """
        self.api_key = api_key or os.environ.get("DAYTONA_API_KEY")
        self.base_url = os.environ.get("DAYTONA_API_BASE", "https://api.daytona.dev")
        self.workspace_id = workspace_id

        if not self.api_key:
            logger.warning("未配置Daytona API密钥")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def create_workspace(self, template: str = "python", name: str = None) -> str:
        """
        创建新的工作区

        Args:
            template: 工作区模板（python, node, go等）
            name: 工作区名称

        Returns:
            str: 工作区ID
        """
        if not self.api_key:
            raise ValueError("Daytona API密钥未配置")

        url = f"{self.base_url}/workspaces"
        data = {
            "template": template,
            "name": name or f"ai-coding-{asyncio.get_event_loop().time()}"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=data) as response:
                    result = await response.json()

                    if response.status == 201:
                        workspace_id = result.get("id")
                        logger.info(f"成功创建Daytona工作区: {workspace_id}")
                        return workspace_id
                    else:
                        error_msg = result.get("error", {}).get("message", "未知错误")
                        raise Exception(f"创建Daytona工作区失败: {error_msg}")

        except aiohttp.ClientError as e:
            logger.error(f"Daytona API网络错误: {e}")
            raise Exception(f"网络连接失败: {e}")
        except Exception as e:
            logger.error(f"创建Daytona工作区失败: {e}")
            raise

    async def execute_code(
        self,
        code: str,
        language: str = "python",
        workspace_id: str = None
    ) -> Dict:
        """
        在Daytona工作区中执行代码

        Args:
            code: 要执行的代码
            language: 编程语言（python, javascript, go等）
            workspace_id: 工作区ID，如果不提供使用默认的

        Returns:
            Dict: 执行结果，包含success, output, error等字段
        """
        if not self.api_key:
            raise ValueError("Daytona API密钥未配置")

        # 使用提供的工作区ID或默认的
        target_workspace = workspace_id or self.workspace_id

        if not target_workspace:
            # 自动创建工作区
            target_workspace = await self.create_workspace(template=language)
            self.workspace_id = target_workspace

        url = f"{self.base_url}/workspaces/{target_workspace}/execute"

        data = {
            "language": language,
            "code": code
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=data, timeout=aiohttp.ClientTimeout(total=120)) as response:
                    result = await response.json()

                    # 检查错误
                    if "error" in result:
                        error_msg = result["error"].get("message", str(result["error"]))
                        logger.error(f"Daytona API错误: {error_msg}")
                        return {
                            'success': False,
                            'error': f"Daytona API错误: {error_msg}",
                            'output': ''
                        }

                    # 检查执行结果
                    if response.status == 200:
                        return {
                            'success': result.get('success', True),
                            'output': result.get('output', ''),
                            'error': result.get('error', ''),
                            'exit_code': result.get('exit_code', 0)
                        }
                    else:
                        return {
                            'success': False,
                            'error': f"HTTP {response.status}: {result}",
                            'output': ''
                        }

        except aiohttp.ClientError as e:
            logger.error(f"Daytona API网络错误: {e}")
            return {
                'success': False,
                'error': f"网络连接失败: {e}",
                'output': ''
            }
        except asyncio.TimeoutError:
            logger.error(f"Daytona API超时")
            return {
                'success': False,
                'error': "执行超时（120秒）",
                'output': ''
            }
        except Exception as e:
            logger.error(f"Daytona执行失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'output': ''
            }

    async def delete_workspace(self, workspace_id: str = None) -> bool:
        """
        删除工作区

        Args:
            workspace_id: 工作区ID，如果不提供使用默认的

        Returns:
            bool: 是否成功删除
        """
        if not self.api_key:
            logger.warning("Daytona API密钥未配置")
            return False

        target_workspace = workspace_id or self.workspace_id

        if not target_workspace:
            return True

        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.base_url}/workspaces/{target_workspace}",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        logger.info(f"成功删除Daytona工作区: {target_workspace}")
                        if target_workspace == self.workspace_id:
                            self.workspace_id = None
                        return True
                    else:
                        logger.warning(f"删除工作区失败: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"删除Daytona工作区失败: {e}")
            return False

    async def get_workspace_info(self, workspace_id: str = None) -> Dict:
        """
        获取工作区信息

        Args:
            workspace_id: 工作区ID

        Returns:
            Dict: 工作区信息
        """
        if not self.api_key:
            raise ValueError("Daytona API密钥未配置")

        target_workspace = workspace_id or self.workspace_id

        if not target_workspace:
            raise ValueError("未指定工作区ID")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/workspaces/{target_workspace}",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        result = await response.json()
                        raise Exception(f"获取工作区信息失败: {result}")

        except Exception as e:
            logger.error(f"获取Daytona工作区信息失败: {e}")
            raise
