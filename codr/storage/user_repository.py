from abc import ABC

from codr.api.schemas.users import UserCreate
from codr.entities import User
from codr.models import UserModel
from codr.storage.storage import SessionLocal


class UserRepository(ABC):
    def get_user(self, user_id):
        raise NotImplementedError

    def create_user(self, user):
        raise NotImplementedError

    def update_user(self, user):
        raise NotImplementedError

    def delete_user(self, user_id):
        raise NotImplementedError


class SqlUserRepository(UserRepository):
    def get_user(self, user_id):
        with SessionLocal() as session:
            user_model = session.query(UserModel).filter_by(id=user_id).first()
            if user_model is None:
                return None
            return User(id=user_model.id, username=user_model.username, github_access_token=user_model.github_access_token)

    def create_user(self, user: UserCreate):
        with SessionLocal() as session:
            user_model = UserModel(username=user.username, github_access_token=None)
            session.add(user_model)
            session.commit()
            return User(id=user_model.id, username=user_model.username)

    def update_user(self, user: User):
        with SessionLocal() as session:
            user_model = session.query(UserModel).filter_by(id=user.id).first()
            if user_model is None:
                return None
            user_model.username = user.username
            user_model.github_access_token = user.github_access_token

            session.commit()
            return User(id=user_model.id, username=user_model.username, github_access_token=user_model.github_access_token)

    def delete_user(self, user_id):
        with SessionLocal() as session:
            user_model = session.query(UserModel).filter_by(id=user_id).first()
            if user_model is None:
                return None
            session.delete(user_model)
            session.commit()
            return User(id=user_model.id, username=user_model.username)


class DummyUserRepository(UserRepository):
    def get_user(self, user_id):
        return User(id=user_id, username="dummy")

    def create_user(self, user):
        return User(id="dummy", username=user.username)

    def update_user(self, user):
        return User(id=user.id, username=user.username)

    def delete_user(self, user_id):
        return User(id=user_id, username="dummy")


def get_user_repository():
    return SqlUserRepository()
