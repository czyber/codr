from codr.storage.user_storage import DummyUserStorage
from codr.user_service import UserService


def get_stub_user_service():
    return UserService(DummyUserStorage())
