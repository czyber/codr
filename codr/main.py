from codr.codebase_service import CodebaseService
from codr.logger import logger
from codr.repo_client import RepoClient
from codr.storage.codebase_storage import SqlCodebaseStorage
from codr.storage.vector_db import ChromaDb

from dataclasses import dataclass


@dataclass
class Task:
    description: str


chroma = ChromaDb()


class AutoCreate:
    def solve_task(self, task: Task, repo_slug: str, token: str):
        repo_client = RepoClient(slug=repo_slug, token=token)
        codebase_service = CodebaseService(storage=SqlCodebaseStorage(), vector_db=chroma, repo_client=repo_client)

        codebase_service.create_embeddings(slug=repo_slug)

        relevant_files = codebase_service.get_relevant_files(task.description)

        code_changes = codebase_service.get_code_changes(task.description, relevant_files)

        codebase_service.apply_code_changes(code_changes=code_changes)


auto_create = AutoCreate()

if __name__ == "__main__":
    logger.info("Starting the service")
    task = Task(description="Remove the `delete_homework` endpoint from the homework_router.")

    auto_create.solve_task(task=task, repo_slug="<your-repo-slug>", token="<your-github-token>")






