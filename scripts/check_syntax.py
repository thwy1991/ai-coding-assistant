# -*- coding: utf-8 -*-
"""
检查Python文件语法
"""

import sys
import os
import py_compile

def check_file(filepath):
    """检查单个文件的语法"""
    try:
        py_compile.compile(filepath, doraise=True)
        print(f"✓ {filepath}")
        return True
    except SyntaxError as e:
        print(f"✗ {filepath}")
        print(f"  语法错误: 第{e.lineno}行: {e.msg}")
        print(f"  {e.text}")
        return False
    except Exception as e:
        print(f"✗ {filepath}")
        print(f"  错误: {e}")
        return False

def main():
    """主函数"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print("=" * 60)
    print("语法检查")
    print("=" * 60)

    # 检查所有Python文件
    python_files = []
    for root, dirs, files in os.walk(project_root):
        # 跳过虚拟环境等目录
        dirs[:] = [d for d in dirs if d not in ['venv', 'env', '__pycache__', '.git']]

        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                python_files.append(filepath)

    print(f"\n找到 {len(python_files)} 个Python文件\n")

    all_ok = True
    for filepath in python_files:
        rel_path = os.path.relpath(filepath, project_root)
        if not check_file(filepath):
            all_ok = False

    print("\n" + "=" * 60)
    if all_ok:
        print("✅ 所有文件语法检查通过！")
    else:
        print("❌ 发现语法错误，请修复后重试")
    print("=" * 60)

    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
