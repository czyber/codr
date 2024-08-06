from fastapi import APIRouter, Depends, HTTPException, status

from codr.api.schemas.github import RepoAdd
from codr.api.schemas.users import CodebaseIndex, User, UserCreate, UserPatch
from codr.application.exceptions import (
    CodebaseIndexAlreadyExistsError,
    NoGitHubAccessTokenError,
    RepoAlreadyExistsError,
)
from codr.application.interactors.codebase.create_index import (
    CreateCodebaseIndex,
    CreateCodebaseIndexRequest,
)
from codr.application.interactors.github.add_repo import AddRepo, AddRepoRequest
from codr.application.interactors.users.create_user import CreateUser, CreateUserRequest
from codr.application.interactors.users.delete_user import DeleteUser, DeleteUserRequest
from codr.application.interactors.users.get_user import GetUser, GetUserRequest
from codr.application.interactors.users.patch_user import PatchUser, PatchUserRequest
from codr.dependencies import Dependencies

router = APIRouter(prefix="/users")


@router.get("/{user_id}", response_model=User)
def get_user(
    user_id: str, get_user_interactor: GetUser = Depends(Dependencies.get_user)
):
    response = get_user_interactor.execute(GetUserRequest(id=user_id))
    if response.user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return response.user



@router.patch("/{user_id}", response_model=User)
def patch_user(
    user_id: str,
    user_patch: UserPatch,
    patch_user_interactor: PatchUser = Depends(Dependencies.patch_user),
):
    response = patch_user_interactor.execute(
        PatchUserRequest(user_id=user_id, patch_user=user_patch)
    )
    return response.user


@router.delete("/{user_id}", response_model=User)
def delete_user(
    user_id: str, delete_user_interactor: DeleteUser = Depends(Dependencies.delete_user)
):
    response = delete_user_interactor.execute(DeleteUserRequest(user_id=user_id))
    return response.user


@router.post("/{user_id}/repos", response_model=str)
def add_repository(
    user_id: str, repo_add: RepoAdd, add_repo: AddRepo = Depends(Dependencies.add_repo)
):
    try:
        response = add_repo.execute(
            AddRepoRequest(owner=repo_add.owner, name=repo_add.name, user_id=user_id)
        )
    except NoGitHubAccessTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have a github access token",
        )
    except RepoAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already has this repo"
        )
    return response.name


@router.post("/{user_id}/codebases/{repo_id}", response_model=CodebaseIndex)
def create_codebase_index(
    user_id: str,
    repo_id: str,
    create_codebase_index_interactor: CreateCodebaseIndex = Depends(
        Dependencies.create_codebase_index
    ),
):
    try:
        response = create_codebase_index_interactor.execute(
            CreateCodebaseIndexRequest(user_id=user_id, repo_id=repo_id)
        )
    except CodebaseIndexAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return CodebaseIndex(repo_id=repo_id)


@router.get("/{user_id}/codebases/{repo_id}", response_model=CodebaseIndex)
def get_codebase_index():
    # TODO: Implement this
    raise NotImplementedError
