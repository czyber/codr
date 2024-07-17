from codr.storage.user_repository import DummyUserRepository
from codr.user_service import UserService


class MockDependencies:
    @staticmethod
    def get_stub_user_service():
        return UserService(DummyUserRepository())
