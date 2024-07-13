from fastapi import APIRouter, Depends

from codr.api.schemas.users import UserCreate, User
from codr.user_service import get_user_service, UserService


router = APIRouter()


@router.post("/users", response_model=User)
def create_user(user_create: UserCreate, user_service: UserService = Depends(get_user_service)):
    return user_service.create_user(user_create)
