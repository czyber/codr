from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from codr.api.schemas.github import GitHubAccessToken, GitHubAccessTokenCreate
from codr.application.entities import VersionControlType
from codr.application.interactors.github.create_access_token import (
    CreateAccessToken,
    CreateAccessTokenRequest,
)
from codr.application.interactors.github.get_redirect_url import (
    GetRedirectURL,
    GetRedirectURLRequest,
)
from codr.dependencies import Dependencies

load_dotenv()

router = APIRouter(prefix="/github")


@router.get("/login")
def login(get_redirect_url: GetRedirectURL = Depends(Dependencies.get_redirect_url)):
    response = get_redirect_url.execute(GetRedirectURLRequest())
    return RedirectResponse(url=response.url)


@router.post("/callback", response_model=GitHubAccessToken)
def github_callback(
    github_access_token_create_interactor: GitHubAccessTokenCreate,
    create_access_token_interactor: CreateAccessToken = Depends(
        Dependencies.create_access_token
    ),
):
    response = create_access_token_interactor.execute(
        CreateAccessTokenRequest(
            code=github_access_token_create_interactor.code,
            user_id=github_access_token_create_interactor.user_id,
        )
    )
    if response.user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return GitHubAccessToken(
        access_token=response.user.get_access_token(VersionControlType.GITHUB)
    )
