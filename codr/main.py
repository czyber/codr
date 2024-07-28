from dataclasses import dataclass

from sqlalchemy import create_engine

from codr.api.routes import app
from codr.codebase_service import CodebaseService
from codr.dependencies import Dependencies
from codr.github_client import GitHubClient
from codr.logger import logger
from codr.models import Base
from codr.storage.codebase_storage import SqlCodebaseStorage
from codr.storage.vector_db import ChromaDb


@dataclass
class Task:
    description: str


class Codr:
    @staticmethod
    def solve_task(task_description: str, repo_slug: str, token: str):
        repo_client = GitHubClient(slug=repo_slug, token=token)
        codebase_service = CodebaseService(
            storage=SqlCodebaseStorage(), vector_db=ChromaDb(), repo_client=repo_client
        )
        codebase_service.create_embeddings(slug=repo_slug)
        relevant_files = codebase_service.get_relevant_files(task_description)
        code_changes = codebase_service.get_code_changes(
            task_description, relevant_files
        )
        codebase_service.apply_code_changes(code_changes=code_changes)


codr = Codr()


if __name__ == "__main__":
    Base.metadata.create_all(bind=create_engine("sqlite:///./test.db"))
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8080)
