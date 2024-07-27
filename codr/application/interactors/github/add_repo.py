from dataclasses import dataclass

from codr.application.entities import Repo
from codr.application.exceptions import NoGitHubAccessTokenError, RepoAlreadyExistsError
from codr.github_client import VersionControlService
from codr.storage.repository import Factory
from codr.storage.user_repository import UserRepository


@dataclass
class AddRepoRequest:
    name: str
    owner: str
    user_id: str


@dataclass
class AddRepoResponse:
    name: str


class AddRepo:
    def __init__(self, version_control_service: VersionControlService, user_repository: UserRepository, repo_factory: Factory[Repo]) -> None:
        self.__version_control_service = version_control_service
        self.__user_repository = user_repository
        self.__repo_factory = repo_factory

    def execute(self, request: AddRepoRequest) -> AddRepoResponse:
        user = self.__user_repository.get(request.user_id)
        if not user.github_access_token:
            raise NoGitHubAccessTokenError("User does not have a github access token")
        user_repo_exists = any(repo.name == request.name and repo.owner == request.owner for repo in user.repos)
        if user_repo_exists:
            raise RepoAlreadyExistsError("User already has this repo")
        self.__version_control_service.set_access_token(user.github_access_token)
        repo = self.__version_control_service.get_repository(f"{request.owner}/{request.name}")
        user.repos.append(repo)
        self.__user_repository.update(user)
        return AddRepoResponse(name=repo.name)
