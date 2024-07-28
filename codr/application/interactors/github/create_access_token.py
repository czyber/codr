import requests
from dataclasses import dataclass

from codr.application.entities import User, VersionControlInfo
from codr.application.interactors.users.get_user import GetUser, GetUserRequest
from codr.application.interactors.users.update_user import UpdateUser, UpdateUserRequest
from codr.utils import GitHubCredentials, RedirectUri
from datetime import datetime, timedelta


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
        if "error" in response_data:
            raise ValueError(f"Error while creating access token for GitHub: {response_data.get('error_description')}")
        access_token = response_data.get("access_token")
        refresh_token = response_data.get("refresh_token")
        access_token_expires_at = datetime.now() + timedelta(seconds=response_data.get("expires_in"))
        refresh_token_expires_at = datetime.now() + timedelta(seconds=response_data.get("refresh_token_expires_in"))
        user = self.__get_user.execute(GetUserRequest(id=request.user_id)).user
        user.version_control_infos.append(VersionControlInfo.create_github(
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expires_at=access_token_expires_at,
            refresh_token_expires_at=refresh_token_expires_at
        ))
        updated_user = self.__update_user.execute(UpdateUserRequest(user=user)).user

        return CreateAccessTokenResponse(user=updated_user)

