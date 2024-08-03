from dataclasses import dataclass

from codr.application.entities import Repo
from codr.application.exceptions import CodebaseIndexAlreadyExistsError
from codr.codebase_service import AbstractCodebaseService
from codr.github_client import VersionControlService
from codr.storage.repo_repository import RepoRepository
from codr.storage.user_repository import UserRepository
from codr.utils import Id


@dataclass
class CreateCodebaseIndexRequest:
    user_id: Id
    repo_id: Id


@dataclass
class CreateCodebaseIndexResponse:
    embeddings: list[str]


@dataclass
class CreateCodebaseIndexPorts:
    version_control_service: VersionControlService
    codebase_service: AbstractCodebaseService
    repo_repository: RepoRepository
    user_repository: UserRepository


class CreateCodebaseIndex:
    def __init__(self, ports: CreateCodebaseIndexPorts) -> None:
        self.__version_control_service = ports.version_control_service
        self.__codebase_service = ports.codebase_service
        self.__repo_repository = ports.repo_repository
        self.__user_repository = ports.user_repository

    def execute(
        self, request: CreateCodebaseIndexRequest
    ) -> CreateCodebaseIndexResponse:
        user = self.__user_repository.get(request.user_id)
        self.__version_control_service.set_user(user.id)

        repo = self.__repo_repository.get(request.repo_id)
        sha = self.__version_control_service.set_repository(repo.identifier)
        if repo.embeddings_created:
            raise CodebaseIndexAlreadyExistsError(
                "Embeddings already created, use GET /users/{user_id}/codebases/{repo_id} to get them."
            )
        if repo.sha != sha:
            repo.sha = sha
            self.__repo_repository.update(repo)

        codebase = self.__version_control_service.repo
        embeddings = self.__codebase_service.create_index(codebase)
        return CreateCodebaseIndexResponse(embeddings=embeddings)
