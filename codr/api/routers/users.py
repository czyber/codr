from fastapi import APIRouter, Depends, HTTPException
from fastapi import status

from codr.api.schemas.users import UserCreate, User
from codr.dependencies import Dependencies
from codr.interactors.users.create_user import CreateUser, CreateUserRequest
from codr.interactors.users.get_user import GetUser, GetUserRequest


router = APIRouter(prefix="/users")


@router.get("/{user_id}", response_model=User)
def get_user(user_id: str, get_user_interactor: GetUser = Depends(Dependencies.get_user)):
    response = get_user_interactor.execute(GetUserRequest(id=user_id))
    if response.user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return response.user


@router.post("", response_model=User)
def create_user(user_create: UserCreate, create_user_interactor: CreateUser = Depends(Dependencies.create_user)):
    response = create_user_interactor.execute(CreateUserRequest(username=user_create.username))
    return response.user

