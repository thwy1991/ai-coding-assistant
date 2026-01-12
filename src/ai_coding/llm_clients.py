# -*- coding: utf-8 -*-
"""
AI Coding Assistant - LLM客户端实现
支持OpenAI、DeepSeek、GLM等多种大语言模型
"""

import os
import logging
from typing import List, Dict, Optional
import aiohttp

logger = logging.getLogger(__name__)


class OpenAIClient:
    """OpenAI API客户端（支持GPT系列）"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = base_url or os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.default_model = "gpt-4"

        if not self.api_key or self.api_key == "your-api-key-here":
            logger.warning("未配置OpenAI API密钥")

        self.client = None
        self._init_client()

    def _init_client(self):
        try:
            import openai
            self.client = openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        except ImportError:
            logger.error("未安装openai包")
        except Exception as e:
            logger.error(f"OpenAI客户端初始化失败: {e}")

    async def chat_completion(self, messages: List[Dict], model: str = None,
                            temperature: float = 0.2, max_tokens: int = 4096) -> str:
        if not self.client:
            raise ValueError("OpenAI客户端未初始化")

        model = model or self.default_model
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {e}")
            raise

    async def generate(self, prompt: str, model: str = None, **kwargs) -> str:
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(messages, model, **kwargs)


class DeepSeekClient:
    """DeepSeek API客户端"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/v1"
        self.default_model = "deepseek-chat"

        if not self.api_key or self.api_key == "your-api-key-here":
            logger.warning("未配置DeepSeek API密钥")

    async def chat_completion(self, messages: List[Dict], model: str = None,
                            temperature: float = 0.2, max_tokens: int = 4096) -> str:
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未配置")

        model = model or self.default_model

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    result = await response.json()

                    # 检查响应是否包含错误
                    if "error" in result:
                        error_msg = result["error"].get("message", str(result["error"]))
                        logger.error(f"DeepSeek API错误: {error_msg}")
                        raise Exception(f"DeepSeek API错误: {error_msg}")

                    # 检查choices字段
                    if "choices" not in result or len(result["choices"]) == 0:
                        logger.error(f"DeepSeek API响应格式异常: {result}")
                        raise Exception("DeepSeek API响应格式异常")

                    return result["choices"][0]["message"]["content"]
        except aiohttp.ClientError as e:
            logger.error(f"DeepSeek API网络错误: {e}")
            raise Exception(f"网络连接失败: {e}")
        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {e}")
            raise

    async def generate(self, prompt: str, model: str = None, **kwargs) -> str:
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(messages, model, **kwargs)


class GLMClient:
    """智谱AI API客户端（GLM系列）"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("ZHIPUAI_API_KEY")
        self.base_url = "https://open.bigmodel.cn/api/paas/v4"
        self.default_model = "glm-4"

        if not self.api_key or self.api_key == "your-api-key-here":
            logger.warning("未配置智谱AI API密钥")

    async def chat_completion(self, messages: List[Dict], model: str = None,
                            temperature: float = 0.2, max_tokens: int = 4096) -> str:
        if not self.api_key:
            raise ValueError("智谱AI API密钥未配置")

        model = model or self.default_model

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    result = await response.json()

                    # 检查响应是否包含错误
                    if "error" in result:
                        error_msg = result["error"].get("message", str(result["error"]))
                        logger.error(f"智谱AI API错误: {error_msg}")
                        raise Exception(f"智谱AI API错误: {error_msg}")

                    # 检查choices字段
                    if "choices" not in result or len(result["choices"]) == 0:
                        logger.error(f"智谱AI API响应格式异常: {result}")
                        raise Exception("智谱AI API响应格式异常")

                    return result["choices"][0]["message"]["content"]
        except aiohttp.ClientError as e:
            logger.error(f"智谱AI API网络错误: {e}")
            raise Exception(f"网络连接失败: {e}")
        except Exception as e:
            logger.error(f"智谱AI API调用失败: {e}")
            raise

    async def generate(self, prompt: str, model: str = None, **kwargs) -> str:
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(messages, model, **kwargs)


class ClaudeClient:
    """Claude API客户端"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.default_model = "claude-3-sonnet-20240229"

        if not self.api_key or self.api_key == "your-api-key-here":
            logger.warning("未配置Claude API密钥")

    async def chat_completion(self, messages: List[Dict], model: str = None,
                            temperature: float = 0.2, max_tokens: int = 4096) -> str:
        if not self.api_key:
            raise ValueError("Claude API密钥未配置")

        model = model or self.default_model

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=headers,
                    json=data
                ) as response:
                    result = await response.json()

                    # 检查响应是否包含错误
                    if "error" in result:
                        error_msg = result["error"].get("message", str(result["error"]))
                        logger.error(f"Claude API错误: {error_msg}")
                        raise Exception(f"Claude API错误: {error_msg}")

                    # 检查content字段
                    if "content" not in result or len(result["content"]) == 0:
                        logger.error(f"Claude API响应格式异常: {result}")
                        raise Exception("Claude API响应格式异常")

                    return result["content"][0]["text"]
        except aiohttp.ClientError as e:
            logger.error(f"Claude API网络错误: {e}")
            raise Exception(f"网络连接失败: {e}")
        except Exception as e:
            logger.error(f"Claude API调用失败: {e}")
            raise

    async def generate(self, prompt: str, model: str = None, **kwargs) -> str:
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(messages, model, **kwargs)


class MockLLMClient:
    """模拟LLM客户端（用于测试）"""

    def __init__(self):
        logger.info("使用MockLLMClient（模拟客户端）")

    async def chat_completion(self, messages: List[Dict], **kwargs) -> str:
        user_message = messages[-1].get("content", "") if messages else ""
        return """```python
print("Hello, World!")
# 这是MockLLMClient返回的示例代码
# 要使用真实的AI功能，请在设置中配置API密钥

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

for i in range(10):
    print(f"fibonacci({i}) = {fibonacci(i)}")
```"""

    async def generate(self, prompt: str, **kwargs) -> str:
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(messages)


# 支持的模型配置
MODEL_CONFIGS = {
    "GPT-4": {
        "provider": "openai",
        "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
        "default": "gpt-4",
        "api_key_env": "OPENAI_API_KEY"
    },
    "Claude": {
        "provider": "claude",
        "models": ["claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-3-opus-20240229"],
        "default": "claude-3-sonnet-20240229",
        "api_key_env": "ANTHROPIC_API_KEY"
    },
    "DeepSeek": {
        "provider": "deepseek",
        "models": ["deepseek-chat", "deepseek-coder"],
        "default": "deepseek-chat",
        "api_key_env": "DEEPSEEK_API_KEY"
    },
    "GLM": {
        "provider": "glm",
        "models": ["glm-4", "glm-3-turbo"],
        "default": "glm-4",
        "api_key_env": "ZHIPUAI_API_KEY"
    },
    "Mock": {
        "provider": "mock",
        "models": ["mock"],
        "default": "mock",
        "api_key_env": None
    }
}


def create_llm_client(provider: str = "openai", api_key: str = None, **kwargs) -> object:
    """
    创建LLM客户端工厂函数

    Args:
        provider: 提供商名称
        api_key: API密钥（可选）
        **kwargs: 其他参数

    Returns:
        LLM客户端实例
    """
    provider = provider.lower()

    if provider == "openai":
        return OpenAIClient(api_key=api_key, **kwargs)
    elif provider == "deepseek":
        return DeepSeekClient(api_key=api_key)
    elif provider == "glm" or provider == "zhipuai":
        return GLMClient(api_key=api_key)
    elif provider == "claude":
        return ClaudeClient(api_key=api_key)
    elif provider == "mock":
        return MockLLMClient()
    else:
        raise ValueError(f"不支持的LLM提供商: {provider}")
