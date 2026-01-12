# -*- coding: utf-8 -*-
"""
测试代码执行器
"""

import asyncio
import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ai_coding.executor.code_executor import CodeExecutor
from ai_coding.executor.multi_language_executor import MultiLanguageExecutor


async def test_python_executor():
    """测试Python代码执行"""
    print("=" * 50)
    print("测试Python代码执行")
    print("=" * 50)

    executor = CodeExecutor(timeout=10)

    # 测试1: 简单的Hello World
    code1 = 'print("Hello, World!")'
    result1 = await executor.execute_python(code1)
    print(f"\n代码: {code1}")
    print(f"结果: {result1}")

    # 测试2: 计算
    code2 = '''
a = 10
b = 20
print(a + b)
'''
    result2 = await executor.execute_python(code2)
    print(f"\n代码: 计算a+b")
    print(f"结果: {result2}")


async def test_multi_language():
    """测试多语言执行"""
    print("\n" + "=" * 50)
    print("测试多语言执行")
    print("=" * 50)

    executor = MultiLanguageExecutor(timeout=10)

    # 测试Python
    python_code = '''
for i in range(3):
    print(f"Python: {i}")
'''
    result = await executor.execute('python', python_code)
    print(f"\nPython结果: {result}")

    # 测试JavaScript
    js_code = '''
for (let i = 0; i < 3; i++) {
    console.log(`JavaScript: ${i}`);
}
'''
    result = await executor.execute('javascript', js_code)
    print(f"\nJavaScript结果: {result}")

    # 测试Bash
    bash_code = '''
echo "Hello from Bash"
echo "Current date: $(date)"
'''
    result = await executor.execute('bash', bash_code)
    print(f"\nBash结果: {result}")


async def main():
    """主测试函数"""
    try:
        await test_python_executor()
        await test_multi_language()
        print("\n" + "=" * 50)
        print("所有测试完成!")
        print("=" * 50)
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
