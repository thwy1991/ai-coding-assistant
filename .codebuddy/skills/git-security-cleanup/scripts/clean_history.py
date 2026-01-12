#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git历史清理工具 - 移除敏感文件并重写历史
"""

import subprocess
import sys
import os

def run_command(cmd, check=True):
    """执行命令"""
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")
    return result

def check_git_repository():
    """检查是否在Git仓库中"""
    result = run_command("git rev-parse --git-dir", check=False)
    return result.returncode == 0

def create_clean_root():
    """创建干净的根提交"""
    print("\n📝 步骤1: 创建新的根提交分支")
    run_command("git checkout --orphan new-root")

    print("\n📝 步骤2: 添加所有文件")
    run_command("git add .")

    print("\n📝 步骤3: 创建干净的提交")
    run_command('git commit -m "Clean initial commit"')

def replace_main_branch():
    """替换主分支"""
    print("\n📝 步骤4: 删除旧的主分支")
    run_command("git branch -D main")

    print("\n📝 步骤5: 重命名新分支为主分支")
    run_command("git branch -m new-root main")

def force_push():
    """强制推送到远程"""
    print("\n📝 步骤6: 强制推送到远程仓库")
    print("⚠️ 警告: 这将重写远程历史！")
    confirm = input("确认要强制推送吗? (yes/no): ")

    if confirm.lower() == 'yes':
        run_command("git push -f origin main")
        print("\n✅ 强制推送成功！")
    else:
        print("\n❌ 已取消推送")
        sys.exit(1)

def verify_cleanup():
    """验证清理结果"""
    print("\n📝 步骤7: 验证清理结果")

    print("\n当前提交历史:")
    run_command("git log --oneline")

    print("\n检查远程仓库:")
    run_command("git remote -v")

def main():
    """主函数"""
    print("=" * 60)
    print("Git历史清理工具")
    print("=" * 60)

    # 检查Git仓库
    if not check_git_repository():
        print("❌ 错误: 当前目录不是Git仓库")
        sys.exit(1)

    # 检查未提交的更改
    result = run_command("git status --porcelain", check=False)
    if result.stdout.strip():
        print("\n⚠️ 警告: 存在未提交的更改")
        print("建议先提交或暂存这些更改")
        response = input("继续吗? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ 已取消")
            sys.exit(1)

    # 显示当前状态
    print("\n当前分支:")
    run_command("git branch")

    print("\n最近的提交:")
    run_command("git log --oneline -5")

    # 执行清理流程
    try:
        create_clean_root()
        replace_main_branch()
        force_push()
        verify_cleanup()

        print("\n" + "=" * 60)
        print("✅ 清理完成！")
        print("=" * 60)
        print("\n后续步骤:")
        print("1. 在GitHub上验证仓库是否干净")
        print("2. 通知团队成员执行: git fetch --all && git reset --hard origin/main")
        print("3. 检查所有敏感信息是否已清除")
        print("4. 使用 scan_secrets.py 扫描确认无敏感信息")

    except Exception as e:
        print(f"\n❌ 错误: {e}", file=sys.stderr)
        print("\n恢复步骤:")
        print("1. 检查错误信息")
        print("2. git checkout main  (切换回原分支)")
        print("3. git branch -D new-root  (删除临时分支)")
        sys.exit(1)

if __name__ == '__main__':
    main()
