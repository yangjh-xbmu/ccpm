#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCPM Issue Close Script

实现类似 ccpm 手动更新任务状态的功能
用法: python issue_close.py <issue_number> [completion_notes]
"""

import os
import sys
import argparse
import logging
import glob
from datetime import datetime, timezone
from dotenv import load_dotenv
from github import Github
import frontmatter

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="标记任务完成并在 GitHub 上关闭对应的 Issue")
    parser.add_argument(
        "issue_number",
        type=int,
        help="要关闭的 Issue 编号")
    parser.add_argument(
        "completion_notes",
        nargs='?',
        default="",
        help="完成说明（可选）")
    return parser.parse_args()


def get_github_repo(token, repo_name):
    """初始化 GitHub 客户端并返回仓库对象"""
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        return repo
    except Exception as e:
        logging.error(f"连接到 GitHub 仓库 '{repo_name}' 失败: {e}")
        sys.exit(1)


def find_local_task_file(issue_number, project_root):
    """查找本地任务文件"""
    # 方法1: 检查新命名方式 .claude/epics/*/{issue_number}.md
    epics_pattern = os.path.join(project_root, "*", f"{issue_number}.md")
    matches = glob.glob(epics_pattern)
    
    if matches:
        return matches[0]
    
    # 方法2: 搜索包含 github:.*issues/{issue_number} 的文件
    for root, dirs, files in os.walk(project_root):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        post = frontmatter.load(f)
                        github_ref = post.metadata.get('github', '')
                        issue_ref = f"issues/{issue_number}"
                        if issue_ref in str(github_ref):
                            return file_path
                except Exception:
                    continue
    
    return None


def update_local_task_status(task_file_path):
    """更新本地任务文件状态"""
    try:
        with open(task_file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        # 获取当前 UTC 时间
        current_datetime = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ")
        
        # 更新 frontmatter
        post.metadata['status'] = 'closed'
        post.metadata['updated'] = current_datetime
        
        # 写回文件
        with open(task_file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        logging.info("已更新本地任务文件状态: %s", task_file_path)
        return True
        
    except Exception as e:
        logging.error("更新本地任务文件失败: %s", e)
        return False


def update_progress_file(task_file_path, issue_number):
    """更新进度文件"""
    try:
        # 从任务文件路径推断 epic 目录
        epic_dir = os.path.dirname(task_file_path)
        
        progress_dir = os.path.join(epic_dir, "updates", str(issue_number))
        progress_file = os.path.join(progress_dir, "progress.md")
        
        if os.path.exists(progress_file):
            with open(progress_file, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            current_datetime = datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ")
            
            # 更新进度信息
            post.metadata['completion'] = 100
            post.metadata['last_sync'] = current_datetime
            
            # 添加完成说明
            completion_note = (f"\n\n## 任务完成\n\n"
                               f"完成时间: {current_datetime}\n状态: 已完成")
            post.content += completion_note
            
            with open(progress_file, 'w', encoding='utf-8') as f:
                f.write(frontmatter.dumps(post))
            
            logging.info("已更新进度文件: %s", progress_file)
            return True
        else:
            logging.info("进度文件不存在，跳过更新: %s", progress_file)
            return True
            
    except Exception as e:
        logging.error("更新进度文件失败: %s", e)
        return False


def close_github_issue(repo, issue_number, completion_notes):
    """在 GitHub 上关闭 Issue"""
    try:
        issue = repo.get_issue(issue_number)
        
        # 添加完成评论
        current_time = datetime.now(timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S UTC")
        
        comment_body = "✅ 任务已完成\n\n"
        if completion_notes:
            comment_body += f"完成说明: {completion_notes}\n\n"
        comment_body += f"---\n关闭时间: {current_time}"
        
        issue.create_comment(comment_body)
        
        # 关闭 Issue
        issue.edit(state='closed')
        
        logging.info("已在 GitHub 上关闭 Issue #%s", issue_number)
        return True
        
    except Exception as e:
        logging.error("关闭 GitHub Issue 失败: %s", e)
        return False


def update_epic_progress(task_file_path, repo):
    """更新 Epic 进度"""
    try:
        # 获取 epic 目录
        epic_dir = os.path.dirname(task_file_path)
        epic_file_path = os.path.join(epic_dir, 'epic.md')
        
        if not os.path.exists(epic_file_path):
            logging.warning("Epic 文件不存在: %s", epic_file_path)
            return False
        
        # 读取 epic 文件获取 GitHub Issue 编号
        with open(epic_file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        epic_issue_number = post.metadata.get('github_issue_number')
        if not epic_issue_number:
            # 尝试从 github 字段提取
            github_ref = post.metadata.get('github', '')
            if 'issues/' in str(github_ref):
                epic_issue_number = str(github_ref).split('issues/')[-1]
        
        if not epic_issue_number:
            logging.warning("无法找到 Epic 的 GitHub Issue 编号")
            return False
        
        # 统计任务进度
        task_files = [f for f in os.listdir(epic_dir)
                      if f.endswith('.md') and f != 'epic.md']
        
        total_tasks = len(task_files)
        closed_tasks = 0
        
        for task_file in task_files:
            task_path = os.path.join(epic_dir, task_file)
            try:
                with open(task_path, 'r', encoding='utf-8') as f:
                    task_post = frontmatter.load(f)
                if task_post.metadata.get('status') == 'closed':
                    closed_tasks += 1
            except Exception:
                continue
        
        # 计算进度百分比
        if total_tasks > 0:
            progress_percentage = int((closed_tasks / total_tasks) * 100)
        else:
            progress_percentage = 0
        
        # 更新本地 epic.md 文件
        post.metadata['progress'] = progress_percentage
        post.metadata['updated'] = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ")
        
        with open(epic_file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        logging.info("Epic 进度已更新: %s%% (%s/%s 任务完成)",
                     progress_percentage, closed_tasks, total_tasks)
        return True
        
    except Exception as e:
        logging.error("更新 Epic 进度失败: %s", e)
        return False


def main():
    """主函数"""
    args = parse_arguments()
    project_root = os.getcwd()
    
    logging.info(f"开始关闭 Issue #{args.issue_number}")
    
    # 加载环境变量
    load_dotenv()
    
    github_token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPO")
    
    if not github_token or not repo_name:
        logging.error("请确保 .env 文件中已配置 GITHUB_TOKEN 和 GITHUB_REPO")
        sys.exit(1)
    
    # 1. 查找本地任务文件
    task_file_path = find_local_task_file(args.issue_number, project_root)
    if not task_file_path:
        logging.error(f"❌ 未找到 Issue #{args.issue_number} 对应的本地任务文件")
        sys.exit(1)
    
    logging.info(f"找到本地任务文件: {task_file_path}")
    
    # 2. 更新本地状态
    if not update_local_task_status(task_file_path):
        logging.error("更新本地任务状态失败")
        sys.exit(1)
    
    # 3. 更新进度文件
    update_progress_file(task_file_path, args.issue_number)
    
    # 4. 连接 GitHub 并关闭 Issue
    repo = get_github_repo(github_token, repo_name)
    if not close_github_issue(repo, args.issue_number, args.completion_notes):
        logging.error("关闭 GitHub Issue 失败")
        sys.exit(1)
    
    # 5. 更新 Epic 进度
    update_epic_progress(task_file_path, repo)
    
    # 6. 输出结果
    print(f"\n✅ 已关闭 Issue #{args.issue_number}")
    print("  本地: 任务标记为完成")
    print("  GitHub: Issue 已关闭")
    if args.completion_notes:
        print(f"  完成说明: {args.completion_notes}")
    print("\n下一步: 运行其他任务或使用 /pm:next 查看下一个优先任务")


if __name__ == "__main__":
    main()