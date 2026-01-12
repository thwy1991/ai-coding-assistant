# -*- coding: utf-8 -*-
"""
测试AI Coding Assistant是否可以正常启动
"""

import sys
import os

# 添加src到路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

print("=" * 60)
print("AI Coding Assistant - 启动测试")
print("=" * 60)
print(f"项目根目录: {project_root}")

try:
    print("\n1. 测试导入LLM客户端...")
    from ai_coding.llm_clients import MockLLMClient
    print("   ✓ MockLLMClient 导入成功")

    print("\n2. 测试导入工作流...")
    from ai_coding.workflow import AICodingWorkflow
    print("   ✓ AICodingWorkflow 导入成功")

    print("\n3. 测试导入执行器...")
    from ai_coding.executor.multi_language_executor import MultiLanguageExecutor
    print("   ✓ MultiLanguageExecutor 导入成功")

    print("\n4. 测试导入代码生成器...")
    from ai_coding.generator.ai_code_generator import AICodeGenerator
    print("   ✓ AICodeGenerator 导入成功")

    print("\n5. 测试导入调试器...")
    from ai_coding.debugger.interactive_debugger import InteractiveDebugger
    print("   ✓ InteractiveDebugger 导入成功")

    print("\n6. 测试导入项目管理器...")
    from ai_coding.manager.project_manager import ProjectManager
    print("   ✓ ProjectManager 导入成功")

    print("\n7. 测试导入安全管理器...")
    from ai_coding.manager.security_manager import SecurityManager
    print("   ✓ SecurityManager 导入成功")

    print("\n8. 初始化MockLLMClient...")
    llm_client = MockLLMClient()
    print("   ✓ MockLLMClient 初始化成功")

    print("\n9. 初始化AICodingWorkflow...")
    workflow = AICodingWorkflow(
        llm_client,
        config={
            'workspace_path': './workspace',
            'sandbox': {'timeout': 30, 'memory_limit': '100m'},
            'security': {'enable_sandbox': True, 'max_code_length': 10000}
        }
    )
    print("   ✓ AICodingWorkflow 初始化成功")

    print("\n10. 测试项目上下文...")
    context = workflow.get_project_context()
    print(f"   ✓ 项目上下文获取成功: {context}")

    print("\n" + "=" * 60)
    print("✅ 所有测试通过！应用可以正常启动。")
    print("=" * 60)

    print("\n启动命令:")
    print("  streamlit run src/ai_coding/frontend/streamlit_app.py")
    print("\n或:")
    print("  python scripts/start_app.py")

    print("\n访问地址:")
    print("  http://localhost:8501")

except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    print("\n请检查错误并修复后重试。")
    sys.exit(1)
