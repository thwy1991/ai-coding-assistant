# -*- coding: utf-8 -*-
"""
AI Coding Assistant - 项目管理器
管理文件系统、项目结构和文件树
"""

import os
import shutil
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ProjectManager:
    """项目管理器，用于管理文件系统和项目结构"""

    def __init__(self, base_path: str = "./workspace"):
        """
        初始化项目管理器

        Args:
            base_path: 项目基础路径
        """
        self.base_path = os.path.abspath(base_path)
        self.current_project = None
        self.file_tree = {}

        # 创建工作区目录
        os.makedirs(self.base_path, exist_ok=True)

        # 初始化文件树
        self._update_file_tree()

    def create_file(self, path: str, content: str = "") -> str:
        """
        创建文件

        Args:
            path: 文件相对路径
            content: 文件内容

        Returns:
            str: 文件完整路径
        """
        full_path = os.path.join(self.base_path, path)

        # 创建目录
        dir_path = os.path.dirname(full_path)
        os.makedirs(dir_path, exist_ok=True)

        # 写入文件
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # 更新文件树
        self._update_file_tree()

        logger.info(f"已创建文件: {full_path}")
        return full_path

    def read_file(self, path: str) -> str:
        """
        读取文件

        Args:
            path: 文件相对路径

        Returns:
            str: 文件内容
        """
        full_path = os.path.join(self.base_path, path)

        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()

    def update_file(self, path: str, content: str) -> str:
        """
        更新文件

        Args:
            path: 文件相对路径
            content: 新的文件内容

        Returns:
            str: 文件完整路径
        """
        full_path = os.path.join(self.base_path, path)

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

        self._update_file_tree()
        logger.info(f"已更新文件: {full_path}")
        return full_path

    def delete_file(self, path: str) -> bool:
        """
        删除文件

        Args:
            path: 文件相对路径

        Returns:
            bool: 是否删除成功
        """
        full_path = os.path.join(self.base_path, path)

        if os.path.exists(full_path):
            os.remove(full_path)
            self._update_file_tree()
            logger.info(f"已删除文件: {full_path}")
            return True
        else:
            logger.warning(f"文件不存在: {full_path}")
            return False

    def create_directory(self, path: str) -> str:
        """
        创建目录

        Args:
            path: 目录相对路径

        Returns:
            str: 目录完整路径
        """
        full_path = os.path.join(self.base_path, path)
        os.makedirs(full_path, exist_ok=True)

        self._update_file_tree()
        logger.info(f"已创建目录: {full_path}")
        return full_path

    def list_files(self, path: str = "", recursive: bool = True) -> List[str]:
        """
        列出文件

        Args:
            path: 相对路径
            recursive: 是否递归列出

        Returns:
            List[str]: 文件列表
        """
        full_path = os.path.join(self.base_path, path)

        if not os.path.exists(full_path):
            return []

        if recursive:
            files = []
            for root, dirs, filenames in os.walk(full_path):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(file_path, self.base_path)
                    files.append(rel_path)
            return files
        else:
            return os.listdir(full_path)

    def get_file_info(self, path: str) -> Dict:
        """
        获取文件信息

        Args:
            path: 文件相对路径

        Returns:
            Dict: 文件信息
        """
        full_path = os.path.join(self.base_path, path)

        if not os.path.exists(full_path):
            return {}

        stat = os.stat(full_path)
        return {
            'path': path,
            'full_path': full_path,
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'created': stat.st_ctime,
            'is_file': os.path.isfile(full_path),
            'is_dir': os.path.isdir(full_path)
        }

    def search_files(self, pattern: str) -> List[str]:
        """
        搜索文件

        Args:
            pattern: 文件名模式（支持通配符）

        Returns:
            List[str]: 匹配的文件列表
        """
        import fnmatch
        matched_files = []

        for root, dirs, files in os.walk(self.base_path):
            for filename in files:
                if fnmatch.fnmatch(filename, pattern):
                    file_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(file_path, self.base_path)
                    matched_files.append(rel_path)

        return matched_files

    def search_in_files(self, content_pattern: str) -> List[Dict]:
        """
        在文件内容中搜索

        Args:
            content_pattern: 内容模式

        Returns:
            List[Dict]: 匹配结果列表，包含文件路径和匹配的行
        """
        import re
        results = []

        for root, dirs, files in os.walk(self.base_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, self.base_path)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()

                    matches = []
                    for i, line in enumerate(lines, 1):
                        if re.search(content_pattern, line):
                            matches.append({
                                'line': i,
                                'content': line.strip()
                            })

                    if matches:
                        results.append({
                            'file': rel_path,
                            'matches': matches
                        })
                except Exception as e:
                    logger.warning(f"无法读取文件 {rel_path}: {e}")

        return results

    def _update_file_tree(self):
        """
        更新项目文件树，用于给AI提供上下文
        """
        file_tree = {}

        for root, dirs, files in os.walk(self.base_path):
            # 跳过隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            rel_root = os.path.relpath(root, self.base_path)
            if rel_root == '.':
                rel_root = ''

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = os.path.join(rel_root, file) if rel_root else file
                full_file_path = os.path.join(root, file)

                try:
                    file_tree[file_path] = {
                        'size': os.path.getsize(full_file_path),
                        'modified': os.path.getmtime(full_file_path),
                        'created': os.path.getctime(full_file_path)
                    }
                except Exception as e:
                    logger.warning(f"无法获取文件信息 {file_path}: {e}")

        self.file_tree = file_tree

    def get_file_tree(self) -> Dict:
        """
        获取文件树

        Returns:
            Dict: 文件树
        """
        return self.file_tree

    def get_file_tree_as_text(self) -> str:
        """
        获取文件树的文本表示

        Returns:
            str: 文件树文本
        """
        lines = []
        for path, info in sorted(self.file_tree.items()):
            lines.append(f"{path} ({info['size']} bytes)")
        return '\n'.join(lines)

    def copy_file(self, src_path: str, dst_path: str) -> str:
        """
        复制文件

        Args:
            src_path: 源文件相对路径
            dst_path: 目标文件相对路径

        Returns:
            str: 目标文件完整路径
        """
        src_full = os.path.join(self.base_path, src_path)
        dst_full = os.path.join(self.base_path, dst_path)

        # 创建目标目录
        os.makedirs(os.path.dirname(dst_full), exist_ok=True)

        # 复制文件
        shutil.copy2(src_full, dst_full)

        self._update_file_tree()
        logger.info(f"已复制文件: {src_full} -> {dst_full}")
        return dst_full

    def move_file(self, src_path: str, dst_path: str) -> str:
        """
        移动文件

        Args:
            src_path: 源文件相对路径
            dst_path: 目标文件相对路径

        Returns:
            str: 目标文件完整路径
        """
        src_full = os.path.join(self.base_path, src_path)
        dst_full = os.path.join(self.base_path, dst_path)

        # 创建目标目录
        os.makedirs(os.path.dirname(dst_full), exist_ok=True)

        # 移动文件
        shutil.move(src_full, dst_full)

        self._update_file_tree()
        logger.info(f"已移动文件: {src_full} -> {dst_full}")
        return dst_full

    def clear_workspace(self):
        """清空工作区"""
        for item in os.listdir(self.base_path):
            item_path = os.path.join(self.base_path, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)

        self._update_file_tree()
        logger.info("已清空工作区")

    def get_project_context(self) -> Dict:
        """
        获取项目上下文信息，用于AI生成代码时提供上下文

        Returns:
            Dict: 项目上下文
        """
        return {
            'base_path': self.base_path,
            'file_tree': self.file_tree,
            'file_count': len(self.file_tree)
        }
