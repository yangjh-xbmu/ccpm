#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCPM Epic 关闭脚本

实现类似 /pm:epic-close 命令的功能，用于关闭已完成的 Epic
"""

import argparse
import os
import sys
import logging
import frontmatter
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from github import Github

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_environment():
    """加载环境变量"""
    load_dotenv()

    github_token = os.getenv('GITHUB_TOKEN')
    github_repo = os.getenv('GITHUB_REPO')

    if not github_token:
        logger.error("未找到 GITHUB_TOKEN 环境变量")
        sys.exit(1)

    if not github_repo:
        logger.error("未找到 GITHUB_REPO 环境变量")
        sys.exit(1)

    return github_token, github_repo


def connect_github(token, repo_name):
    """连接到 GitHub"""
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        return repo
    except Exception as e:
        logger.error(f"连接 GitHub 失败: {e}")
        sys.exit(1)


def find_epic_directory(epic_name):
    """查找 Epic 目录"""
    epic_path = Path(epic_name)
    if not epic_path.exists():
        logger.error(f"Epic 目录不存在: {epic_path}")
        return None

    epic_file = epic_path / 'epic.md'
    if not epic_file.exists():
        logger.error(f"Epic 文件不存在: {epic_file}")
        return None

    return epic_path


def check_all_tasks_completed(epic_path):
    """检查所有任务是否已完成"""
    open_tasks = []

    # 排除的文件名列表
    excluded_files = {'epic.md', 'github-mapping.md', 'README.md'}

    for md_file in epic_path.glob('*.md'):
        if md_file.name in excluded_files:
            continue

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)

            status = post.metadata.get('status', 'open')
            if status != 'closed':
                open_tasks.append(md_file.name)
        except Exception as e:
            logger.warning(f"读取任务文件失败 {md_file}: {e}")
            open_tasks.append(md_file.name)

    return open_tasks


def update_epic_status(epic_path):
    """更新 Epic 状态"""
    epic_file = epic_path / 'epic.md'
    current_datetime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    try:
        with open(epic_file, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        # 更新元数据
        post.metadata['status'] = 'completed'
        post.metadata['progress'] = '100%'
        post.metadata['updated'] = current_datetime
        post.metadata['completed'] = current_datetime

        # 写回文件
        with open(epic_file, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))

        logger.info(f"已更新 Epic 状态: {epic_file}")
        return True

    except Exception as e:
        logger.error(f"更新 Epic 状态失败: {e}")
        return False


def close_epic_on_github(repo, epic_issue_number, completion_notes):
    """在 GitHub 上关闭 Epic Issue"""
    try:
        issue = repo.get_issue(epic_issue_number)

        # 添加完成评论
        comment_body = f"✅ Epic 已完成 - 所有任务都已完成\n\n{completion_notes}"
        issue.create_comment(comment_body)

        # 关闭 Issue
        issue.edit(state='closed')

        logger.info(f"已在 GitHub 上关闭 Epic Issue #{epic_issue_number}")
        return True

    except Exception as e:
        logger.error(f"关闭 GitHub Epic Issue 失败: {e}")
        return False


def get_epic_github_issue_number(epic_path):
    """获取 Epic 的 GitHub Issue 编号"""
    epic_file = epic_path / 'epic.md'

    try:
        with open(epic_file, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        return post.metadata.get('github_issue_number')

    except Exception as e:
        logger.warning(f"读取 Epic GitHub Issue 编号失败: {e}")
        return None


def count_completed_tasks(epic_path):
    """统计已完成的任务数量"""
    task_count = 0

    # 排除的文件名列表
    excluded_files = {'epic.md', 'github-mapping.md', 'README.md'}

    for md_file in epic_path.glob('*.md'):
        if md_file.name not in excluded_files:
            task_count += 1

    return task_count


def calculate_duration(epic_path):
    """计算 Epic 持续时间"""
    epic_file = epic_path / 'epic.md'

    try:
        with open(epic_file, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        created = post.metadata.get('created')
        completed = post.metadata.get('completed')

        if created and completed:
            created_dt = datetime.fromisoformat(
                created.replace('Z', '+00:00')
            )
            completed_dt = datetime.fromisoformat(
                completed.replace('Z', '+00:00')
            )
            duration = (completed_dt - created_dt).days
            return duration

    except Exception as e:
        logger.warning(f"计算持续时间失败: {e}")

    return None


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='关闭已完成的 CCPM Epic',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python epic_close.py simple-flask-app "所有功能已实现并测试通过"
  python epic_close.py user-auth "用户认证系统开发完成"
        """
    )

    parser.add_argument(
        'epic_name',
        help='Epic 名称（目录名）'
    )

    parser.add_argument(
        'completion_notes',
        help='Epic 完成说明'
    )

    args = parser.parse_args()

    logger.info(f"开始关闭 Epic: {args.epic_name}")

    # 1. 查找 Epic 目录
    epic_path = find_epic_directory(args.epic_name)
    if not epic_path:
        sys.exit(1)

    # 2. 检查所有任务是否已完成
    open_tasks = check_all_tasks_completed(epic_path)
    if open_tasks:
        logger.error(f"❌ 无法关闭 Epic。还有未完成的任务: {', '.join(open_tasks)}")
        sys.exit(1)

    # 3. 更新 Epic 状态
    if not update_epic_status(epic_path):
        sys.exit(1)

    # 4. 在 GitHub 上关闭 Epic（如果有 Issue 编号）
    github_token, github_repo = load_environment()
    repo = connect_github(github_token, github_repo)

    epic_issue_number = get_epic_github_issue_number(epic_path)
    if epic_issue_number:
        close_epic_on_github(repo, epic_issue_number, args.completion_notes)
    else:
        logger.warning("无法找到 Epic 的 GitHub Issue 编号")

    # 5. 输出结果
    task_count = count_completed_tasks(epic_path)
    duration = calculate_duration(epic_path)

    print(f"\n✅ Epic 已关闭: {args.epic_name}")
    print(f"  已完成任务: {task_count}")
    if duration is not None:
        print(f"  持续时间: {duration} 天")
    print(f"  完成说明: {args.completion_notes}")
    print("\n下一步: 运行 /pm:next 查看下一个优先工作")


if __name__ == '__main__':
    main()
