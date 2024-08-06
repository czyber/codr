from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from codr.application.entities import Repo, User
from codr.application.interactors.codebase.create_index import (
    CreateCodebaseIndex,
    CreateCodebaseIndexPorts,
)
from codr.application.interactors.github.add_repo import AddRepo
from codr.application.interactors.github.authenticate_user import AuthenticateUser
from codr.application.interactors.github.create_access_token import CreateAccessToken
from codr.application.interactors.github.get_redirect_url import GetRedirectURL
from codr.application.interactors.github.refresh_access_token import RefreshAccessToken
from codr.application.interactors.users.create_user import CreateUser
from codr.application.interactors.users.delete_user import DeleteUser
from codr.application.interactors.users.get_user import GetUser
from codr.application.interactors.users.patch_user import PatchUser
from codr.application.interactors.users.update_user import UpdateUser
from codr.codebase_service import AbstractCodebaseService, CodebaseService
from codr.github_client import GitHubClient, VersionControlService
from codr.models import Base, RepoModel, UserModel
from codr.storage.dao.sql_dao import SqlDAO
from codr.storage.mapper.repo import MapperRepo
from codr.storage.mapper.user import MapperUser
from codr.storage.repo_repository import RepoRepository
from codr.storage.repository import Factory
from codr.storage.user_repository import UserRepository
from codr.storage.vector_db import ChromaDb, VectorDb


class SessionSingleton:
    __session = None

    @staticmethod
    def get_session() -> Session:
        if SessionSingleton.__session is None:
            engine = create_engine("sqlite:///foo.db")
            Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            Base.metadata.create_all(bind=engine)
            SessionSingleton.__session = Session()
        return SessionSingleton.__session


class Dependencies:
    @staticmethod
    def user_factory() -> Factory:
        return Factory(User)

    @staticmethod
    def repo_factory() -> Factory:
        return Factory(Repo)

    @staticmethod
    def user_repository() -> UserRepository:
        return UserRepository(
            dao=SqlDAO(
                session=SessionSingleton.get_session(),
                model=UserModel,
                mapper=MapperUser(),
            ),
            factory=Dependencies.user_factory(),
        )

    @staticmethod
    def get_user() -> GetUser:
        return GetUser(user_repository=Dependencies.user_repository())

    @staticmethod
    def update_user() -> UpdateUser:
        return UpdateUser(user_repository=Dependencies.user_repository())


    @staticmethod
    def delete_user() -> DeleteUser:
        return DeleteUser(user_repository=Dependencies.user_repository())

    @staticmethod
    def patch_user() -> PatchUser:
        return PatchUser(user_repository=Dependencies.user_repository())

    @staticmethod
    def get_redirect_url() -> GetRedirectURL:
        return GetRedirectURL()

    @staticmethod
    def create_access_token() -> CreateAccessToken:
        return CreateAccessToken(
            get_user=Dependencies.get_user(), update_user=Dependencies.update_user()
        )

    @staticmethod
    def refresh_access_token() -> RefreshAccessToken:
        return RefreshAccessToken(
            get_user=Dependencies.get_user(), update_user=Dependencies.update_user()
        )

    @staticmethod
    def authenticate_user() -> AuthenticateUser:
        return AuthenticateUser(
            create_access_token=Dependencies.create_access_token(),
            refresh_access_token=Dependencies.refresh_access_token(),
            get_user=Dependencies.get_user(),
        )

    @staticmethod
    def version_control_service() -> VersionControlService:
        return GitHubClient(authenticate_user=Dependencies.authenticate_user())

    @staticmethod
    def add_repo() -> AddRepo:
        return AddRepo(
            version_control_service=Dependencies.version_control_service(),
            user_repository=Dependencies.user_repository(),
            repo_factory=Dependencies.repo_factory(),
        )

    @staticmethod
    def repo_repository() -> RepoRepository:
        return RepoRepository(
            dao=SqlDAO(
                session=SessionSingleton.get_session(),
                model=RepoModel,
                mapper=MapperRepo(),
            ),
            factory=Dependencies.repo_factory(),
        )

    @staticmethod
    def vector_db() -> VectorDb:
        return ChromaDb()

    @staticmethod
    def codebase_service() -> AbstractCodebaseService:
        return CodebaseService(
            storage=Dependencies.repo_repository(), vector_db=Dependencies.vector_db()
        )

    @staticmethod
    def create_codebase_index() -> CreateCodebaseIndex:
        ports = CreateCodebaseIndexPorts(
            version_control_service=Dependencies.version_control_service(),
            codebase_service=Dependencies.codebase_service(),
            repo_repository=Dependencies.repo_repository(),
            user_repository=Dependencies.user_repository(),
        )
        return CreateCodebaseIndex(ports=ports)
