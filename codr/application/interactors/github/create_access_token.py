import requests
from dataclasses import dataclass

from codr.application.entities import User
from codr.application.interactors.users.get_user import GetUser, GetUserRequest
from codr.application.interactors.users.update_user import UpdateUser, UpdateUserRequest
from codr.utils import GitHubCredentials, RedirectUri
from codr.storage.user_repository import UserRepository


@dataclass
class CreateAccessTokenRequest:
    code: str
    user_id: str


@dataclass
class CreateAccessTokenResponse:
    user: User


class CreateAccessToken:
    def __init__(self, get_user: GetUser, update_user: UpdateUser) -> None:
        self.__update_user = update_user
        self.__get_user = get_user

    def execute(self, request: CreateAccessTokenRequest) -> CreateAccessTokenResponse:
        github_credentials = GitHubCredentials.load()
        redirect_uri = RedirectUri.load()
        token_url = "https://github.com/login/oauth/access_token"
        headers = {"Accept": "application/json"}
        data = {
            "client_id": github_credentials.client_id,
            "client_secret": github_credentials.client_secret,
            "code": request.code,
            "redirect_uri": redirect_uri.uri,
        }

        response = requests.post(token_url, headers=headers, data=data)
        response_data = response.json()
        access_token = response_data.get("access_token")
        user = self.__get_user.execute(GetUserRequest(id=request.user_id)).user
        user.github_access_token = access_token
        updated_user = self.__update_user.execute(UpdateUserRequest(user=user)).user

        return CreateAccessTokenResponse(user=updated_user)

