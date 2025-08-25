import os
import sys
import argparse
import logging
from dotenv import load_dotenv
from github import Github
import frontmatter

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Synchronize a local epic and its tasks to GitHub Issues.")
    parser.add_argument(
        "epic_name",
        help="The name of the epic to synchronize (e.g., 'simple-flask-app')."
    )
    return parser.parse_args()


def get_github_repo(token, repo_name):
    """Initializes the GitHub client and returns the repository object."""
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        return repo
    except Exception as e:
        logging.error(
            f"Failed to connect to GitHub repo '{repo_name}': {e}"
        )
        sys.exit(1)


def create_epic_issue(repo, epic_name, project_root):
    """Creates the main Epic issue from the epic.md file."""
    logging.info(f"Creating Epic Issue for '{epic_name}'...")
    epic_file_path = os.path.join(project_root, epic_name, 'epic.md')

    if not os.path.exists(epic_file_path):
        logging.error(f"Epic file not found at '{epic_file_path}'")
        return None

    try:
        with open(epic_file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        # 优先使用 frontmatter 中的 name 字段，然后是 title 字段
        epic_title = (post.metadata.get('name') or
                      post.metadata.get('title'))

        # 如果 frontmatter 中没有标题，尝试从内容中提取第一个 H1 标题
        if not epic_title:
            import re
            h1_match = re.search(r'^#\s+(.+)$', post.content, re.MULTILINE)
            if h1_match:
                epic_title = h1_match.group(1).strip()
            else:
                epic_title = 'No Title'

        title = f"[EPIC] {epic_title}"
        labels = post.metadata.get('labels', [])
        if 'epic' not in labels:
            labels.append('epic')

        issue = repo.create_issue(
            title=title,
            body=post.content,
            labels=labels
        )
        return issue

    except Exception as e:
        logging.error(f"Failed to create epic issue: {e}")
        return None


def create_task_issues(repo, epic_name, project_root, epic_issue):
    """
    Scans the epic directory for task files and creates a GitHub issue for each.
    Returns a map of old filenames to new issue numbers.
    """
    logging.info(f"Starting to create task issues for epic '{epic_name}'...")
    epic_dir = os.path.join(project_root, epic_name)
    if not os.path.isdir(epic_dir):
        logging.error(f"Epic directory not found at '{epic_dir}'")
        sys.exit(1)

    task_files = [
        f for f in os.listdir(epic_dir) if f.endswith('.md') and f != 'epic.md'
    ]
    if not task_files:
        logging.warning(f"No task files found in '{epic_dir}'.")
        return {}

    file_to_issue_map = {}

    for task_file in task_files:
        try:
            task_path = os.path.join(epic_dir, task_file)
            task_post = frontmatter.load(task_path)

            # 优先使用 frontmatter 中的 name 字段，然后是 title 字段
            task_title = (task_post.metadata.get('name') or
                          task_post.metadata.get('title'))

            # 如果 frontmatter 中没有标题，尝试从内容中提取第一个 H1 或 H2 标题
            if not task_title:
                import re
                h_match = re.search(r'^#{1,2}\s+(.+)$',
                                    task_post.content, re.MULTILINE)
                if h_match:
                    task_title = h_match.group(1).strip()
                else:
                    task_title = 'No Title'

            title = task_title
            labels = task_post.metadata.get('labels', [])
            if 'task' not in labels:
                labels.append('task')

            body = (
                f"Parent Epic: #{epic_issue.number}\n\n---\n\n{task_post.content}"
            )

            issue = repo.create_issue(
                title=title,
                body=body,
                labels=labels
            )

            logging.info(
                f"Successfully created task issue #{issue.number} "
                f"for '{task_file}'"
            )
            file_to_issue_map[task_file] = issue.number

        except Exception as e:
            logging.error(
                f"Failed to create issue for task file '{task_file}': {e}"
            )
            continue

    logging.info("Finished creating all task issues.")
    return file_to_issue_map


def rename_and_update_task_files(epic_name, project_root, file_to_issue_map):
    """
    重命名本地任务文件为对应的 Issue 编号，并更新其元数据。
    """
    logging.info("开始重命名本地任务文件并更新元数据...")
    epic_dir = os.path.join(project_root, epic_name)

    if not file_to_issue_map:
        logging.warning("没有需要重命名的文件。")
        return

    for old_filename, issue_number in file_to_issue_map.items():
        try:
            old_path = os.path.join(epic_dir, old_filename)
            new_filename = f"{issue_number}.md"
            new_path = os.path.join(epic_dir, new_filename)

            # 重命名文件
            os.rename(old_path, new_path)
            logging.info(f"文件 '{old_filename}' 已重命名为 '{new_filename}'")

            # 更新文件元数据
            with open(new_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)

            post.metadata['github_issue_number'] = issue_number

            with open(new_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter.dumps(post))

            logging.info(
                f"已更新 '{new_filename}' 的元数据，"
                f"添加了 github_issue_number: {issue_number}"
            )

        except Exception as e:
            logging.error(f"处理文件 '{old_filename}' 时出错: {e}")
            continue

    logging.info("所有任务文件均已重命名和更新完毕。")


def update_epic_file_and_issue(epic_name, project_root, epic_issue):
    """
    更新本地 epic.md 文件和远程 Epic Issue，追加任务列表。
    """
    logging.info(
        f"开始更新 Epic 文件和 Issue #{epic_issue.number} 的任务列表..."
    )
    epic_dir = os.path.join(project_root, epic_name)
    task_files = [
        f for f in os.listdir(epic_dir)
        if f.endswith('.md') and f != 'epic.md'
    ]

    if not task_files:
        logging.info("没有找到任务文件，无需更新 Epic。")
        return

    task_list_md = []
    for filename in sorted(task_files):
        try:
            issue_number = os.path.splitext(filename)[0]
            task_path = os.path.join(epic_dir, filename)
            with open(task_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                # 使用与创建 Issue 时相同的标题提取逻辑
                task_title = (post.metadata.get('name') or
                              post.metadata.get('title'))

                # 如果 frontmatter 中没有标题，尝试从内容中提取第一个 H1 或 H2 标题
                if not task_title:
                    import re
                    h_match = re.search(r'^#{1,2}\s+(.+)$',
                                        post.content, re.MULTILINE)
                    if h_match:
                        task_title = h_match.group(1).strip()
                    else:
                        task_title = '无标题任务'

                task_list_md.append(f"- [ ] {task_title} (#{issue_number})")
        except Exception as e:
            logging.error(f"读取任务文件 '{filename}' 时出错: {e}")

    if not task_list_md:
        logging.warning("未能生成任务列表。")
        return

    task_section = "\n\n## Tasks\n\n" + "\n".join(task_list_md)

    # 更新本地 epic.md 文件
    try:
        epic_file_path = os.path.join(epic_dir, 'epic.md')
        with open(epic_file_path, 'a', encoding='utf-8') as f:
            f.write(task_section)
        logging.info(f"已更新本地 '{epic_file_path}' 文件，追加了任务列表。")
    except Exception as e:
        logging.error(f"更新本地 epic.md 文件时出错: {e}")

    # 更新远程 GitHub Issue
    try:
        original_body = epic_issue.body if epic_issue.body else ""
        new_body = original_body + task_section
        epic_issue.edit(body=new_body)
        logging.info(f"已更新 GitHub Issue #{epic_issue.number}，追加了任务列表。")
    except Exception as e:
        logging.error(f"更新 GitHub Issue #{epic_issue.number} 时出错: {e}")


def create_github_mapping_file(
    epic_name, project_root, epic_issue, file_to_issue_map
):
    """
    在 Epic 目录下创建一个 github-mapping.md 文件，
    记录任务文件与 GitHub Issue 的映射关系。
    """
    logging.info("开始创建 github-mapping.md 文件...")
    epic_dir = os.path.join(project_root, epic_name)
    mapping_file_path = os.path.join(epic_dir, 'github-mapping.md')

    try:
        with open(mapping_file_path, 'w', encoding='utf-8') as f:
            f.write(f"# Epic: {epic_issue.title} (#{epic_issue.number})\n\n")
            f.write("## Task to GitHub Issue Mapping\n\n")
            f.write("| Original File Name | GitHub Issue |\n")
            f.write("|--------------------|--------------|\n")
            for filename, issue_number in file_to_issue_map.items():
                f.write(f"| {filename} | #{issue_number} |\n")
        logging.info(f"成功创建映射文件: '{mapping_file_path}'")
    except Exception as e:
        logging.error(f"创建映射文件时出错: {e}")


def main():
    """程序主入口，驱动 epic 同步流程。"""
    args = parse_arguments()
    project_root = os.getcwd()  # 假设脚本从项目根目录运行
    logging.info(f"开始同步 Epic: {args.epic_name}")

    # 从 .env 文件加载环境变量
    load_dotenv()

    github_token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPO")

    if not github_token or not repo_name:
        logging.error(
            "请确保 .env 文件中已配置 GITHUB_TOKEN 和 GITHUB_REPO。"
        )
        sys.exit(1)

    logging.info(f"成功加载仓库配置: {repo_name}")

    repo = get_github_repo(github_token, repo_name)
    logging.info(f"成功连接到仓库: {repo.full_name}")

    epic_issue = create_epic_issue(repo, args.epic_name, project_root)
    if epic_issue:
        logging.info(
            f"成功创建 Epic Issue #{epic_issue.number}: "
            f"'{epic_issue.title}'"
        )
        task_issue_map = create_task_issues(
            repo, args.epic_name, project_root, epic_issue
        )
        if task_issue_map:
            logging.info("任务 Issues 创建完成。")
            logging.info(f"文件与 Issue 编号映射: {task_issue_map}")
            rename_and_update_task_files(
                args.epic_name, project_root, task_issue_map
            )
            update_epic_file_and_issue(
                args.epic_name, project_root, epic_issue
            )
            create_github_mapping_file(
                args.epic_name, project_root, epic_issue, task_issue_map
            )
        else:
            logging.warning("没有创建任何任务 Issues。")


# --- 主程序执行 --- #
if __name__ == "__main__":
    logging.info("开始执行 epic-sync 脚本...")
    main()
