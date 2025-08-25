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
        "epic_name", help="The name of the epic to synchronize (e.g., 'simple-flask-app').")
    return parser.parse_args()


def get_github_repo(token, repo_name):
    """Initializes the Github instance and returns the repository object."""
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        return repo
    except Exception as e:
        logging.error(
            f"Failed to connect to GitHub or find repo {repo_name}: {e}")
        sys.exit(1)


def main():
    """Main function to drive the epic-sync process."""
    args = parse_arguments()
    logging.info(f"Epic to synchronize: {args.epic_name}")

    # Load environment variables from .env file
    load_dotenv()

    github_token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPO")

    if not github_token or not repo_name:
        logging.error(
            "GITHUB_TOKEN and GITHUB_REPO must be set in the .env file.")
        sys.exit(1)

    logging.info(
        f"Successfully loaded configuration for repository: {repo_name}")

    repo = get_github_repo(github_token, repo_name)
    logging.info(f"Successfully connected to repository: {repo.full_name}")


# --- Main execution --- #
if __name__ == "__main__":
    logging.info("Starting epic-sync process...")
    main()
