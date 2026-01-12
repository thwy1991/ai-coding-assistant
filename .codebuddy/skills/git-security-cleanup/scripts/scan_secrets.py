#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扫描Git仓库中的敏感信息
"""

import os
import re
import sys
from pathlib import Path

# 敏感信息模式
SENSITIVE_PATTERNS = {
    'OpenAI API Key': r'sk-[a-zA-Z0-9]{20,}',
    'DeepSeek API Key': r'sk-[a-zA-Z0-9]{20,}',
    'Daytona API Key': r'dtn_[a-zA-Z0-9]{40,}',
    'JWT Token': r'eyJ[a-zA-Z0-9_-]{100,}',
    'Database String': r'(mongodb|mysql|postgres|redis)://[^\s"\'<]+',
    'Password Assignment': r'password\s*=\s*[^\s"\']{8,}',
    'API Key Assignment': r'api[_-]?key\s*=\s*[^\s"\']{20,}',
    'Secret Assignment': r'secret\s*=\s*[^\s"\']{10,}',
    'Token Assignment': r'token\s*=\s*[^\s"\']{20,}',
    'AWS Key': r'AKIA[0-9A-Z]{16}',
    'Private Key Header': r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----',
    'Certificate Header': r'-----BEGIN\s+CERTIFICATE-----',
}

# 需要忽略的文件/目录
IGNORE_PATTERNS = [
    r'\.git/',
    r'node_modules/',
    r'\.venv/',
    r'venv/',
    r'__pycache__/',
    r'\.egg-info/',
    r'\.pyc$',
    r'\.example$',
    r'test_.*\.py$',
    r'\.codebuddy/',
]

def should_ignore(path):
    """检查是否应该忽略该文件"""
    for pattern in IGNORE_PATTERNS:
        if re.search(pattern, str(path)):
            return True
    return False

def scan_file(filepath):
    """扫描单个文件"""
    findings = []

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        for name, pattern in SENSITIVE_PATTERNS.items():
            matches = re.finditer(pattern, content)
            for match in matches:
                findings.append({
                    'type': name,
                    'line': content[:match.start()].count('\n') + 1,
                    'pattern': match.group(0)[:50] + '...' if len(match.group(0)) > 50 else match.group(0)
                })

    except Exception as e:
        pass  # 忽略无法读取的文件

    return findings

def scan_directory(directory):
    """扫描整个目录"""
    all_findings = []

    for root, dirs, files in os.walk(directory):
        # 移除应该忽略的目录
        dirs[:] = [d for d in dirs if not any(re.search(p, d) for p in IGNORE_PATTERNS)]

        for filename in files:
            filepath = Path(root) / filename

            if should_ignore(filepath):
                continue

            findings = scan_file(filepath)
            if findings:
                all_findings.append({
                    'file': str(filepath.relative_to(directory)),
                    'findings': findings
                })

    return all_findings

def print_report(findings):
    """打印扫描报告"""
    if not findings:
        print("✅ 未发现敏感信息")
        return

    print("\n" + "=" * 60)
    print("⚠️ 发现敏感信息！")
    print("=" * 60)

    for item in findings:
        print(f"\n📄 文件: {item['file']}")
        for finding in item['findings']:
            print(f"  • 类型: {finding['type']}")
            print(f"    行号: {finding['line']}")
            print(f"    内容: {finding['pattern']}")

    print("\n" + "=" * 60)
    print("🔧 建议:")
    print("=" * 60)
    print("1. 移除或替换敏感信息")
    print("2. 更新 .gitignore 文件")
    print("3. 使用环境变量而非硬编码")
    print("4. 如果已提交，使用 git filter-branch 清理历史")

def main():
    """主函数"""
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'

    print(f"🔍 扫描目录: {directory}")
    findings = scan_directory(directory)

    print_report(findings)

    # 返回退出码
    sys.exit(1 if findings else 0)

if __name__ == '__main__':
    main()
