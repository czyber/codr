from dataclasses import dataclass

import requests

from codr.application.entities import SetTokenRequest, User, VersionControlType
from codr.application.interactors.users.get_user import GetUser, GetUserRequest
from codr.application.interactors.users.update_user import UpdateUser, UpdateUserRequest
from codr.utils import GitHubCredentials, Id


@dataclass
class RefreshAccessTokenRequest:
    user_id: Id
    version_control_type: VersionControlType = VersionControlType.GITHUB


@dataclass
class RefreshAccessTokenResponse:
    user: User


class RefreshAccessToken:
    def __init__(self, get_user: GetUser, update_user: UpdateUser) -> None:
        self.__update_user = update_user
        self.__get_user = get_user

    def execute(self, request: RefreshAccessTokenRequest) -> RefreshAccessTokenResponse:
        user = self.__get_user.execute(GetUserRequest(request.user_id)).user
        if not user:
            raise ValueError("User not found")

        refresh_token = user.get_refresh_token(request.version_control_type)
        if not refresh_token:
            raise ValueError(
                "User does not have a refresh token for the specified version control type"
            )

        github_credentials = GitHubCredentials.load()
        token_url = "https://github.com/login/oauth/access_token"
        headers = {"Accept": "application/json"}
        data = {
            "client_id": github_credentials.client_id,
            "client_secret": github_credentials.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        response = requests.post(token_url, headers=headers, data=data)
        response_data = response.json()
        if "error" in response_data:
            raise ValueError(
                f"Error while refreshing access token for GitHub: {response_data.get('error_description')}"
            )
        access_token = response_data.get("access_token")
        refresh_token = response_data.get("refresh_token")
        expires_in = response_data.get("expires_in")
        refresh_token_expires_in = response_data.get("refresh_token_expires_in")

        user.set_access_token(
            SetTokenRequest(
                version_control_type=request.version_control_type,
                access_token=access_token,
                refresh_token=refresh_token,
                access_token_expires_in=expires_in,
                refresh_token_expires_in=refresh_token_expires_in,
            )
        )

        updated_user = self.__update_user.execute(UpdateUserRequest(user=user)).user
        return RefreshAccessTokenResponse(user=updated_user)
