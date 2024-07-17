from codr.api.schemas.users import UserCreate
from codr.storage.user_repository import UserRepository, SqlUserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(self, user: UserCreate):
        return self.user_repository.create_user(user)

    def get_user(self, user_id):
        return self.user_repository.get_user(user_id)

    def update_user(self, user):
        return self.user_repository.update_user(user)

    def delete_user(self, user_id):
        return self.user_repository.delete_user(user_id)


def get_user_service():
    return UserService(SqlUserRepository())
