from fastapi import APIRouter, Depends, status
from src.schema.user import UserRequest, Token, UserCreate, UserLogin, UserResponse, RefreshToken
from src.services.user import get_user_service, UserService
from fastapi.security import HTTPBearer
from src.utils.jwt import TokenData, get_current_active_user
from typing import Annotated
router = APIRouter(prefix="/auth", tags=["user"])

oauth2_scheme = HTTPBearer()


@router.post('/create_user', response_model=UserRequest)
async def user_create(form_data: UserCreate, current_user: Annotated[TokenData, Depends(get_current_active_user)],
                      user_service: UserService = Depends(get_user_service)):
    return await user_service.create_user(form_data, current_user)


@router.post("/login", response_model=Token)
async def login(login_request: UserLogin, user_service: UserService = Depends(get_user_service)):
    return await user_service.login_for_access_token(login_request.email, login_request.password)

@router.post("/refresh", status_code=status.HTTP_200_OK)
async def get_new_access_token(refresh_token: RefreshToken, user_service: UserService = Depends(get_user_service)):
    return await user_service.refresh_access_token(refresh_token)


@router.get("/user-info", response_model=UserResponse)
async def get_current_user(current_user: Annotated[TokenData, Depends(get_current_active_user)], user_service: UserService = Depends(get_user_service)):
    return await user_service.get_user_info(current_user)
