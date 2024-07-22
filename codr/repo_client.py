import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import git
from github import Github, Auth
from github.Repository import Repository
import requests

from codr.logger import logger
from dotenv import load_dotenv

from codr.models import new_uuid

load_dotenv()

uuid = new_uuid()[:5]
new_branch_name = f"new-branch-{uuid}"


class GitHubClient:
    def __init__(self, slug: str, token: str):
        self.__github = Github(auth=Auth.Token(token))
        self.__repo = self._get_repository(slug=slug)
        self.__token = token

    def _get_repository(self, slug: str) -> Repository:
        logger.info(f"Getting repository {slug}")
        return self.__github.get_repo(slug)

    @property
    def repo(self) -> Repository:
        return self.__repo

    @property
    def default_branch(self) -> str:
        return self.__repo.default_branch

    @property
    def sha(self) -> str:
        return self.__repo.get_branch(self.__repo.default_branch).commit.sha

    @property
    def repo_slug(self) -> str:
        return self.__repo.full_name

    @property
    def tarball_url(self) -> str:
        return f"https://api.github.com/repos/{self.repo_slug}/tarball/{self.sha}"

    def download(self):
        base_temp_dir = '/tmp'
        if not os.path.exists(base_temp_dir):
            print(f"Base temp directory does not exist: {base_temp_dir}")
        else:
            print(f"Base temp directory exists: {base_temp_dir}")
            if os.access(base_temp_dir, os.W_OK):
                print(f"Base temp directory is writable: {base_temp_dir}")
            else:
                print(f"Base temp directory is not writable: {base_temp_dir}")
        logger.info(f"Downloading repository {self.repo_slug} at {self.sha}")
        try:
            tmp_dir = tempfile.mkdtemp(dir=base_temp_dir, prefix=self.sha)
            logger.debug(f"Temporary directory created at: {tmp_dir}")
        except FileNotFoundError as fnf_error:
            logger.error(f"FileNotFoundError: {fnf_error}")
            logger.error(f"Directory creation failed. Path attempted: {os.path.join(base_temp_dir, self.sha)}")
        except PermissionError as perm_error:
            logger.error(f"PermissionError: {perm_error}")
            logger.error(f"Check permissions for directory: {base_temp_dir}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        else:
            logger.debug(f"Custom temp directory is not writable or does not exist: {base_temp_dir}")
        tmp_repo_dir = os.path.join(tmp_dir, "repo")
        os.makedirs(tmp_repo_dir, exist_ok=True)
        logger.info(f"Created temporary directory {tmp_repo_dir}")

        # Clean the directory
        for root, dirs, files in os.walk(tmp_repo_dir, topdown=False):
            for name in files:
                if name.endswith('.py'):
                    os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

        tarfile_path = os.path.join(tmp_dir, f"{self.sha}.tar.gz")

        response = requests.get(self.tarball_url, stream=True, headers={"Authorization": f"Bearer {self.__token}", "X-GitHub-Api-Version": "2022-11-28", "Accept": "application/vnd.github+json"})
        logger.info(f"Downloading tarball from {self.tarball_url}")
        if response.status_code == 200:
            with open(tarfile_path, "wb") as f:
                f.write(response.content)
        else:
            raise Exception(
                f"Failed to get tarball url for {self.tarball_url}. Please check if the repository exists and the provided token is valid."
            )

        with tarfile.open(tarfile_path, "r:gz") as tar:
            tar.extractall(path=tmp_repo_dir)  # extract all members normally
            extracted_folders = [
                name
                for name in os.listdir(tmp_repo_dir)
                if os.path.isdir(os.path.join(tmp_repo_dir, name))
            ]
            if extracted_folders:
                root_folder = extracted_folders[0]  # assuming the first folder is the root folder
                root_folder_path = os.path.join(tmp_repo_dir, root_folder)
                for item in os.listdir(root_folder_path):
                    s = os.path.join(root_folder_path, item)
                    d = os.path.join(tmp_repo_dir, item)
                    if os.path.isdir(s):
                        shutil.move(
                            s, d
                        )  # move all directories from the root folder to the output directory
                    elif s.endswith('.py'):
                        # Skipping symlinks to prevent FileNotFoundError.
                        if not os.path.islink(s):
                            shutil.copy2(
                                s, d
                            )  # copy all .py files from the root folder to the output directory

                shutil.rmtree(root_folder_path)  # remove the root folder

        logger.info(f"Download complete. Extracted files to {tmp_repo_dir}")

        return tmp_dir, tmp_repo_dir

    def initialize_git_repo(self, repo_path: str):
        # Initialize the repository
        self.run_command("git init", repo_path)

        # Add the remote repository
        remote_url = f"https://czyber:<token>@github.com/czyber/atheneum-api.git"
        self.run_command(f"git remote add origin {remote_url}", repo_path)

        # Fetch all branches and commits
        self.run_command("git fetch origin", repo_path)

        # Clean up untracked files before checkout
        self.run_command("git clean -fd", repo_path)

        # Checkout the specific commit SHA
        self.run_command(f"git checkout {self.sha}", repo_path)

        # Create a new branch from the commit
        self.run_command(f"git checkout -fb {new_branch_name}", repo_path)
        logger.info(f"Git repository initialized in {repo_path}")

    def commit_changes(self, repo_path: str):
        logger.info(f"Committing changes in {repo_path}")
        # Add all changes to the staging area
        self.run_command("git add .", repo_path)

        # Commit the changes
        try:
            commit_output = self.run_command('git commit -m "Commit changes"', repo_path)
            logger.info(f"Git commit output:\n{commit_output}")
        except Exception as e:
            logger.error(f"Commit failed: {e}")
            raise

    def create_pull_request(self, repo_path: str):
        logger.info(f"Creating a pull request in {repo_path}")
        # Push the changes to the remote repository
        self.run_command(f"git push origin {new_branch_name}", repo_path)

        # Create a pull request
        pr = self.__repo.create_pull(
            title="Pull request from Python script",
            body="This is an automated pull request created by a Python script.",
            head=new_branch_name,
            base=self.default_branch
        )
        logger.info(f"Pull request created in {repo_path}")

    def run_command(self, command, cwd):
        result = subprocess.run(command, cwd=cwd, text=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.debug(f"Command stdout: {result.stdout}")
        if result.returncode != 0:
            logger.error(f"Command stderr: {result.stderr}")
            raise Exception(f"Command failed: {command}\nError: {result.stderr}")
        return result.stdout
