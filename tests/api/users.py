from unittest import TestCase

from fastapi.testclient import TestClient

from codr.api.routes import app
from codr.user_service import get_user_service
from tests.utils import get_stub_user_service

app.dependency_overrides[get_user_service] = get_stub_user_service
client = TestClient(app)


class TestUsers(TestCase):
