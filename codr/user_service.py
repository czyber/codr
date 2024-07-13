from codr.api.schemas.users import UserCreate
from codr.storage.user_storage import UserStorage, SqlUserStorage


class UserService:
    def __init__(self, user_storage: UserStorage):
        self.user_storage = user_storage

    def create_user(self, user: UserCreate):
        return self.user_storage.create_user(user)

    def get_user(self, user_id):
        return self.user_storage.get_user(user_id)

    def update_user(self, user):
        return self.user_storage.update_user(user)

    def delete_user(self, user_id):
        return self.user_storage.delete_user(user_id)


def get_user_service():
    return UserService(SqlUserStorage())
