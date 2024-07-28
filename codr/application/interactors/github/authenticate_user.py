from dataclasses import dataclass

from codr.application.entities import VersionControlType, User
from codr.application.interactors.github.create_access_token import CreateAccessToken, CreateAccessTokenRequest
from codr.application.interactors.github.refresh_access_token import RefreshAccessToken, RefreshAccessTokenRequest
from codr.application.interactors.users.get_user import GetUser, GetUserRequest


@dataclass
class AuthenticateUserRequest:
    user_id: str
    version_control_type: VersionControlType


@dataclass
class AuthenticateUserResponse:
    access_token: str


class AuthenticateUser:
    def __init__(self,
                 create_access_token: CreateAccessToken,
                 refresh_access_token: RefreshAccessToken,
                 get_user: GetUser
                 ) -> None:
        self.__create_access_token = create_access_token
        self.__refresh_access_token = refresh_access_token
        self.__get_user = get_user

    def execute(self, request: AuthenticateUserRequest) -> AuthenticateUserResponse:
        user = self.__get_user.execute(GetUserRequest(id=request.user_id)).user
        if not user:
            raise ValueError("User not found")

        # Cases:
        # 1. User has no access token
        # 2. User has an expired access token
        # 3. User has a valid access token
        access_token = user.get_access_token(request.version_control_type)
        if not access_token:
            access_token = self.__create_access_token.execute(CreateAccessTokenRequest(code="", user_id=request.user_id)).user.get_access_token(request.version_control_type)
        else:
            # Refresh access token if it is expired
            if not user.has_valid_access_token(request.version_control_type):
                access_token = self.__refresh_access_token.execute(RefreshAccessTokenRequest(user_id=request.user_id, version_control_type=request.version_control_type)).user.get_access_token(request.version_control_type)

        return AuthenticateUserResponse(access_token=access_token)
