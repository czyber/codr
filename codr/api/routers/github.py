
from fastapi import APIRouter, HTTPException, Depends

from dotenv import load_dotenv
from fastapi import status
from fastapi.responses import RedirectResponse

from codr.api.schemas.github import GitHubAccessTokenCreate, GitHubAccessToken
from codr.dependencies import Dependencies
from codr.application.interactors.github.create_access_token import CreateAccessToken, CreateAccessTokenRequest
from codr.application.interactors.github.get_redirect_url import GetRedirectURL, GetRedirectURLRequest

load_dotenv()

router = APIRouter()


@router.get("/login")
def login(get_redirect_url: GetRedirectURL = Depends(Dependencies.get_redirect_url)):
    response = get_redirect_url.execute(GetRedirectURLRequest())
    return RedirectResponse(url=response.url)


@router.post("/github/callback", response_model=GitHubAccessToken)
def github_callback(
        github_access_token_create_interactor: GitHubAccessTokenCreate,
        create_access_token_interactor: CreateAccessToken = Depends(Dependencies.create_access_token)
):
    response = create_access_token_interactor.execute(CreateAccessTokenRequest(code=github_access_token_create_interactor.code, user_id=github_access_token_create_interactor.user_id))
    if response.user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return GitHubAccessToken(user=response.user)
