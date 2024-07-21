from dataclasses import dataclass
import os
from typing import Any, TypeVar

from dotenv import load_dotenv

load_dotenv()


Kwargs = dict[str, Any]
Id = str
IdType = TypeVar('IdType', bound=Id)


@dataclass
class GitHubCredentials:
    client_id: str
    client_secret: str

    @classmethod
    def load(cls) -> "GitHubCredentials":
        return cls(
            client_id=os.getenv("GITHUB_CLIENT_ID"),
            client_secret=os.getenv("GITHUB_CLIENT_SECRET")
        )


@dataclass
class RedirectUri:
    uri: str

    @classmethod
    def load(cls) -> "RedirectUri":
        return cls(uri=os.getenv("REDIRECT_URI"))
