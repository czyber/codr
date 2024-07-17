from codr.storage.user_repository import UserRepository, SqlUserRepository
from codr.interactors.github.create_access_token import CreateAccessToken
from codr.interactors.github.get_redirect_url import GetRedirectURL
from codr.interactors.users.create_user import CreateUser
from codr.interactors.users.get_user import GetUser
from codr.interactors.users.update_user import UpdateUser


class Dependencies:
    @staticmethod
    def user_repository() -> UserRepository:
        return SqlUserRepository()

    @staticmethod
    def get_user() -> GetUser:
        return GetUser(user_repository=Dependencies.user_repository())

    @staticmethod
    def update_user() -> UpdateUser:
        return UpdateUser(user_repository=Dependencies.user_repository())

    @staticmethod
    def create_user() -> CreateUser:
        return CreateUser(user_repository=Dependencies.user_repository())

    @staticmethod
    def get_redirect_url() -> GetRedirectURL:
        return GetRedirectURL()

    @staticmethod
    def create_access_token() -> CreateAccessToken:
        return CreateAccessToken(
            get_user=Dependencies.get_user(),
            update_user=Dependencies.update_user()
        )
