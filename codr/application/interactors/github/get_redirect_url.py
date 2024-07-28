from dataclasses import dataclass

from codr.logger import logger
from codr.utils import GitHubCredentials


@dataclass
class GetRedirectURLRequest:
    pass


@dataclass
class GetRedirectURLResponse:
    url: str


class GetRedirectURL:
    def execute(self, request: GetRedirectURLRequest) -> GetRedirectURLResponse:
        github_credentials = GitHubCredentials.load()
        github_auth_url = f"https://github.com/login/oauth/authorize?client_id={github_credentials.client_id}&scope=repo"
        logger.info(f"Redirecting to {github_auth_url}")
        return GetRedirectURLResponse(url=github_auth_url)
