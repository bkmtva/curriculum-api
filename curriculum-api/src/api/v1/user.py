from http import HTTPStatus
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Body, status, Header
from typing import Optional
from datetime import datetime

from orjson import orjson
from pydantic import BaseModel, EmailStr, UUID4
from typing import List
from src.schema.utils import orjson_dumps
import uuid
from typing import Optional
from src.schema.user import UserRequest, UserInDB, Token, UserCreate, UserLogin, UserResponse
from src.services.user import get_user_service, UserService
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Annotated
router = APIRouter(prefix="/auth", tags=["user"])


@router.post('/create_user', response_model=UserRequest)
async def user_create(form_data: UserCreate, user_service: UserService = Depends(get_user_service)):
    return await user_service.create_user(form_data)


@router.post("/login", response_model=Token)
async def login(login_request: UserLogin, user_service: UserService = Depends(get_user_service)):
    return await user_service.login_for_access_token(login_request.email, login_request.password)

@router.get("/refresh", status_code=status.HTTP_200_OK)
async def get_new_access_token(token: str, user_service: UserService = Depends(get_user_service)):
    return await user_service.refresh_access_token(token)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/user-info", response_model=UserResponse)
async def get_current_user(token: str = Depends(oauth2_scheme), user_service: UserService = Depends(get_user_service)):
    print("аоптьоуктпк", token)
    return await user_service.get_user_info(token)
