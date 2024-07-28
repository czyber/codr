import os
from dataclasses import dataclass
from typing import Any, TypeVar

from dotenv import load_dotenv

load_dotenv()


Kwargs = dict[str, Any]
Id = str
IdType = TypeVar("IdType", bound=Id)


def get_env_var(name: str) -> str:
    env_var = os.getenv(name)
    if env_var is None:
        raise ValueError(f"Environment variable {name} not set")
    return env_var


@dataclass
class GitHubCredentials:
    client_id: str
    client_secret: str

    @classmethod
    def load(cls) -> "GitHubCredentials":
        client_id = get_env_var("GITHUB_CLIENT_ID")
        client_secret = get_env_var("GITHUB_CLIENT_SECRET")
        return cls(
            client_id=client_id,
            client_secret=client_secret,
        )


@dataclass
class RedirectUri:
    uri: str

    @classmethod
    def load(cls) -> "RedirectUri":
        uri = get_env_var("REDIRECT_URI")
        return cls(uri=uri)
