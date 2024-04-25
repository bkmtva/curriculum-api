from fastapi import APIRouter, Depends, status, UploadFile, File, Body, Form, HTTPException
from src.schema import user as user_schema
from src.services.user import get_user_service, UserService
from fastapi.security import HTTPBearer
from src.utils.jwt import TokenData, ResetTokenData, get_current_active_user, logout_current_user, get_current_reset_email
from typing import Annotated, Optional, Union, List
from pydantic import BaseModel, Json
router = APIRouter(prefix="/auth", tags=["auth"])
from dataclasses import dataclass
oauth2_scheme = HTTPBearer()
# class TestModel(BaseModel):
#     a: int = 1
#     b: str = ''
#
#     class Config:
#         schema_extra = {
#             "example": {
#                 "a": 42,
#                 "b": "example string"
#             }
#         }


# @router.post("/form")
# def endpoint(model: Annotated[Json[TestModel], Form]= TestModel().json(),
#         profile_image: Optional[Union[UploadFile, str]] = '',):
#     return model



@router.post("/login", response_model=user_schema.Token)
async def login(
        login_request: user_schema.UserLogin,
        user_service: UserService = Depends(get_user_service)
):
    return await user_service.login_for_access_token(login_request.email, login_request.password)


@router.delete("/logout")
async def logout(current_user: Annotated[TokenData, Depends(get_current_active_user)],
                loggout_message: Annotated[TokenData, Depends(logout_current_user)],):
    return loggout_message


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def get_new_access_token(refresh_token: user_schema.RefreshToken, user_service: UserService = Depends(get_user_service)):
    return await user_service.refresh_access_token(refresh_token)


@router.get("/user-info", response_model=user_schema.UserDetailSchema)
async def get_current_user(current_user: Annotated[TokenData, Depends(get_current_active_user)], user_service: UserService = Depends(get_user_service)):
    return await user_service.get_by_id(current_user.user_id)


@router.post('/password/reset/request/')
async def password_reset_request(password_reset_request: user_schema.PasswordResetRequest, user_service: UserService = Depends(get_user_service)) -> dict:
    return await user_service.send_email(password_reset_request)

@router.post('/password/reset/validate/')
async def password_reset_validate(token_data: Annotated[ResetTokenData, Depends(get_current_reset_email)]) -> dict:
    return {"reset_token": token_data.reset_token}

@router.post('/password/reset/new_password/')
async def password_reset_new(new_password_data: user_schema.PasswordResetNewPassword, token_data: Annotated[ResetTokenData, Depends(get_current_reset_email)], user_service: UserService = Depends(get_user_service)) -> dict:
    return await user_service.change_password(new_password_data, token_data.email)
