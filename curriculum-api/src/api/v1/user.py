from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Body, status, Header

from src.schema.user import UserRequest, UserInDB, Token, UserCreate
from src.services.user import get_user_service, UserService
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["user"])


@router.post('/create_user', response_model=UserRequest)
async def user_create(form_data: UserCreate, user_service: UserService = Depends(get_user_service)):
    return await user_service.create_user(form_data)


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), user_service: UserService = Depends(get_user_service)):
    return user_service.login_for_access_token(form_data)




