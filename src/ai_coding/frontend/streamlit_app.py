# -*- coding: utf-8 -*-
"""
AI Coding Assistant - Streamlit前端界面
提供用户友好的Web界面，支持多模型切换
"""

import streamlit as st
from typing import Optional
import asyncio
import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.ai_coding.workflow import AICodingWorkflow
from src.ai_coding.llm_clients import (
    create_llm_client,
    MODEL_CONFIGS,
    OpenAIClient,
    DeepSeekClient,
    GLMClient,
    ClaudeClient,
    MockLLMClient
)


def get_llm_client_from_config(model_family: str, model_name: str, api_key: str = None):
    """
    根据配置创建LLM客户端

    Args:
        model_family: 模型系列（GPT-4, Claude, DeepSeek等）
        model_name: 具体模型名称
        api_key: API密钥
    """
    config = MODEL_CONFIGS.get(model_family, MODEL_CONFIGS["Mock"])

    # 使用传入的API密钥或从环境变量获取
    if not api_key:
        api_key = os.environ.get(config.get("api_key_env", ""), "")

    if not api_key and model_family != "Mock":
        st.warning(f"⚠️ 未配置{model_family} API密钥，使用Mock模式")

    # 创建客户端
    try:
        return create_llm_client(
            provider=config["provider"],
            api_key=api_key
        )
    except Exception as e:
        st.error(f"创建LLM客户端失败: {e}")
        return MockLLMClient()


def init_session_state():
    """初始化Session State"""
    if 'assistant' not in st.session_state:
        # 默认模型配置
        if 'model_family' not in st.session_state:
            st.session_state.model_family = "GPT-4"
        if 'model_name' not in st.session_state:
            st.session_state.model_name = "gpt-4"
        if 'execution_mode' not in st.session_state:
            st.session_state.execution_mode = "auto"
        if 'auto_execute' not in st.session_state:
            st.session_state.auto_execute = True

        # 获取LLM客户端
        llm_client = get_llm_client_from_config(
            st.session_state.model_family,
            st.session_state.model_name
        )

        # 创建AI助手
        st.session_state.assistant = AICodingWorkflow(
            llm_client,
            config={
                'workspace_path': './workspace',
                'sandbox': {
                    'timeout': 30,
                    'memory_limit': '100m',
                    'execution_mode': st.session_state.execution_mode
                },
                'security': {'enable_sandbox': True, 'max_code_length': 10000}
            }
        )
        st.session_state.llm_client = llm_client
        st.session_state.history = []
        st.session_state.current_code = ""


def recreate_assistant_with_new_model(model_family: str, model_name: str, execution_mode: str = None):
    """
    切换模型后重新创建助手

    Args:
        model_family: 模型系列
        model_name: 模型名称
        execution_mode: 执行模式
    """
    # 获取新的客户端
    new_client = get_llm_client_from_config(model_family, model_name)

    # 保存当前代码和历史
    current_code = st.session_state.current_code
    history = st.session_state.history

    # 重新创建助手
    st.session_state.llm_client = new_client
    st.session_state.assistant = AICodingWorkflow(
        new_client,
        config={
            'workspace_path': './workspace',
            'sandbox': {
                'timeout': 30,
                'memory_limit': '100m',
                'execution_mode': execution_mode or st.session_state.execution_mode
            },
            'security': {'enable_sandbox': True, 'max_code_length': 10000}
        }
    )

    # 恢复状态
    st.session_state.current_code = current_code
    st.session_state.history = history
    st.session_state.model_family = model_family
    st.session_state.model_name = model_name
    if execution_mode:
        st.session_state.execution_mode = execution_mode

    st.success(f"✅ 已切换到 {model_family} - {model_name}")


def run_app():
    """运行Streamlit应用"""
    st.set_page_config(
        page_title="AI Coding Assistant",
        page_icon="🤖",
        layout="wide"
    )

    st.title("🤖 AI Coding Assistant")
    st.markdown("类似Claude Code的代码执行能力，支持多语言代码生成、执行和调试")

    # 初始化
    init_session_state()

    # 侧边栏
    with st.sidebar:
        st.header("⚙️ 设置")

        # 模型选择
        st.subheader("🤖 AI模型配置")

        # 模型系列选择
        model_family = st.selectbox(
            "模型系列",
            list(MODEL_CONFIGS.keys()),
            index=0,
            key="model_family_select"
        )

        # 根据模型系列获取可用模型
        model_config = MODEL_CONFIGS.get(model_family, {})
        available_models = model_config.get("models", ["mock"])

        # 具体模型选择
        model_name = st.selectbox(
            "具体模型",
            available_models,
            index=0,
            key="model_name_select"
        )

        # API密钥配置
        if model_family != "Mock":
            api_key_env = model_config.get("api_key_env")
            st.caption(f"环境变量: {api_key_env}")

            # 提供API密钥输入
            api_key_input = st.text_input(
                "API密钥（可选，覆盖环境变量）",
                type="password",
                placeholder="输入API密钥...",
                key=f"api_key_{model_family}"
            )
        else:
            api_key_input = None

        # 切换模型按钮
        if st.button("🔄 切换模型", key="switch_model"):
            recreate_assistant_with_new_model(model_family, model_name)
            st.rerun()

        st.divider()

        # 显示当前模型
        st.info(f"当前模型: **{st.session_state.get('model_family', 'N/A')} - {st.session_state.get('model_name', 'N/A')}**")

        st.divider()

        # 语言选择
        st.subheader("💻 编程语言")
        language = st.selectbox(
            "选择语言",
            ["python", "javascript", "java", "go", "rust", "bash", "cpp", "c"],
            index=0,
            key="language_select"
        )

        # 执行模式
        st.subheader("🎯 执行模式")

        execution_mode = st.selectbox(
            "代码执行方式",
            ["auto", "local", "docker", "daytona"],
            index=0,
            help="auto: 自动选择（优先Docker）\nlocal: 本地执行\ndocker: Docker容器\ndaytona: 云端沙箱（需要API密钥）",
            key="execution_mode_select"
        )

        # Daytona配置
        if execution_mode == "daytona":
            st.caption("🔗 Daytona API配置")
            daytona_api_key = st.text_input(
                "Daytona API密钥",
                type="password",
                placeholder="输入Daytona API密钥...",
                value=os.environ.get("DAYTONA_API_KEY", ""),
                key="daytona_api_key"
            )
            daytona_api_base = st.text_input(
                "Daytona API地址",
                placeholder="https://api.daytona.dev",
                value=os.environ.get("DAYTONA_API_BASE", "https://api.daytona.dev"),
                key="daytona_api_base"
            )

            # 设置环境变量
            if daytona_api_key:
                os.environ["DAYTONA_API_KEY"] = daytona_api_key
            if daytona_api_base:
                os.environ["DAYTONA_API_BASE"] = daytona_api_base

        # 自动执行选项
        auto_execute = st.checkbox(
            "🚀 代码生成后自动执行",
            value=True,
            help="勾选后，生成的代码会自动执行"
        )

        # 功能模式
        mode = st.radio(
            "功能模式",
            ["生成代码", "执行代码", "调试代码"],
            horizontal=True,
            key="mode_select"
        )

        # 显示项目文件树
        st.header("📁 项目文件")
        file_tree = st.session_state.assistant.project_manager.get_file_tree_as_text()
        if file_tree:
            st.text(file_tree)
        else:
            st.info("工作区为空")

        # 清空工作区
        if st.button("清空工作区"):
            st.session_state.assistant.project_manager.clear_workspace()
            st.session_state.history = []
            st.rerun()

    # 主界面
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("💬 对话区")

        # 显示当前代码编辑区
        st.markdown("#### 📝 代码编辑区")
        edited_code = st.text_area(
            "当前代码（可编辑）",
            value=st.session_state.current_code,
            height=300,
            key="code_editor",
            help="在这里编辑或查看生成的代码"
        )
        st.session_state.current_code = edited_code

        # 执行按钮
        col_exec1, col_exec2 = st.columns([1, 1])
        with col_exec1:
            if st.button("▶️ 执行当前代码", use_container_width=True):
                if not edited_code.strip():
                    st.warning("⚠️ 代码为空，请先输入或生成代码")
                else:
                    with st.spinner(f"正在{execution_mode}模式下执行..."):
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            result = loop.run_until_complete(
                                st.session_state.assistant.executor.execute(
                                    language=language,
                                    code=edited_code
                                )
                            )

                            # 显示执行结果
                            if result['success']:
                                st.success(f"✅ 执行成功！")
                                if result.get('output'):
                                    st.info(f"📤 输出:\n{result['output']}")
                            else:
                                st.error(f"❌ 执行失败: {result.get('error', '未知错误')}")

                            # 添加到历史记录
                            st.session_state.history.append({
                                "user": "执行代码",
                                "assistant": {
                                    'action': 'execute',
                                    'code': edited_code,
                                    'output': result.get('output', ''),
                                    'error': result.get('error', ''),
                                    'success': result['success']
                                }
                            })
                        except Exception as e:
                            st.error(f"❌ 执行错误: {e}")
                        finally:
                            loop.close()

        with col_exec2:
            if st.button("🗑️ 清空代码", use_container_width=True):
                st.session_state.current_code = ""
                st.rerun()

        st.divider()

        # 显示对话历史
        if st.session_state.history:
            for msg in st.session_state.history:
                with st.chat_message("user"):
                    st.write(msg["user"])

                with st.chat_message("assistant"):
                    if isinstance(msg["assistant"], dict):
                        # 显示代码
                        if 'code' in msg['assistant']:
                            st.code(msg['assistant']['code'], language=msg['assistant'].get('language', 'python'))

                        # 显示输出
                        if 'output' in msg['assistant'] and msg['assistant']['output']:
                            st.info(f"📤 输出:\n{msg['assistant']['output']}")

                        # 显示错误
                        if 'error' in msg['assistant'] and msg['assistant']['error']:
                            st.error(f"❌ 错误:\n{msg['assistant']['error']}")

                        # 显示文件创建
                        if 'file_path' in msg['assistant']:
                            st.success(f"📄 已创建文件: {msg['assistant']['file_path']}")
                    else:
                        st.write(msg["assistant"])

        # 用户输入
        user_input = st.chat_input("输入你的代码需求...")

        if user_input:
            # 处理请求
            with st.spinner("思考中..."):
                # 构建上下文
                context = {
                    'language': language,
                    'code': st.session_state.current_code
                }

                # 异步处理请求
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                try:
                    # 如果启用了自动执行，且模式为执行代码
                    if auto_execute and mode == "执行代码":
                        # 使用执行模式
                        context['should_execute'] = True
                    else:
                        context['should_execute'] = False

                    response = loop.run_until_complete(
                        st.session_state.assistant.handle_request(user_input, context)
                    )

                    # 如果启用了自动执行且生成了代码，自动执行
                    if auto_execute and 'code' in response and not response.get('output'):
                        with st.spinner(f"正在{execution_mode}模式下执行代码..."):
                            exec_result = loop.run_until_complete(
                                st.session_state.assistant.executor.execute(
                                    language=language,
                                    code=response['code']
                                )
                            )
                            response['output'] = exec_result.get('output', '')
                            response['error'] = exec_result.get('error', '')
                            response['executed'] = True
                finally:
                    loop.close()

            # 更新当前代码
            if 'code' in response:
                st.session_state.current_code = response['code']

            # 添加到历史
            st.session_state.history.append({"user": user_input, "assistant": response})

            # 刷新页面
            st.rerun()

    with col2:
        st.subheader("💻 代码编辑器")

        # 显示当前代码
        current_code = st.text_area(
            "当前代码",
            value=st.session_state.current_code,
            height=400,
            key="code_editor",
            placeholder=f"在此输入{language}代码..."
        )

        # 更新当前代码
        if current_code != st.session_state.current_code:
            st.session_state.current_code = current_code

        # 执行按钮
        if st.button("▶️ 执行代码", type="primary"):
            with st.spinner("执行中..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                try:
                    result = loop.run_until_complete(
                        st.session_state.assistant.executor.execute(language, current_code)
                    )
                finally:
                    loop.close()

                # 显示结果
                if result['success']:
                    st.success("✅ 执行成功")
                    if result['output']:
                        st.info(f"📤 输出:\n{result['output']}")
                else:
                    st.error(f"❌ 执行失败:\n{result['error']}")

                    # 提供自动修复选项
                    if st.button("🔧 自动修复"):
                        with st.spinner("修复中..."):
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)

                            try:
                                debug_result = loop.run_until_complete(
                                    st.session_state.assistant.debugger.debug_and_fix(
                                        current_code, result['error'], language
                                    )
                                )
                            finally:
                                loop.close()

                            if debug_result['success']:
                                st.success("✅ 修复成功")
                                st.session_state.current_code = debug_result['fixed_code']
                                st.code(debug_result['fixed_code'], language=language)
                                st.rerun()
                            else:
                                st.error(f"❌ 修复失败: {debug_result.get('error', '未知错误')}")

        # 保存到文件
        if st.button("💾 保存到文件"):
            filename = st.text_input("文件名", value=f"output.{language}")
            if filename:
                file_path = st.session_state.assistant.project_manager.create_file(
                    filename, current_code
                )
                st.success(f"已保存到: {file_path}")

        # 优化代码
        if st.button("⚡ 优化代码"):
            with st.spinner("优化中..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                try:
                    optimized_code = loop.run_until_complete(
                        st.session_state.assistant.code_generator.optimize_code(
                            current_code, language
                        )
                    )
                finally:
                    loop.close()

                st.session_state.current_code = optimized_code
                st.success("✅ 优化完成")
                st.code(optimized_code, language=language)
                st.rerun()

        # 生成测试
        if st.button("🧪 生成测试"):
            with st.spinner("生成测试..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                try:
                    test_code = loop.run_until_complete(
                        st.session_state.assistant.code_generator.generate_tests(
                            current_code, language
                        )
                    )
                finally:
                    loop.close()

                st.success("✅ 测试生成完成")
                st.code(test_code, language=language)

    # 页脚
    st.markdown("---")
    st.markdown("💡 提示：请先配置真实的LLM API（如OpenAI）以获得最佳体验")


if __name__ == "__main__":
    run_app()
