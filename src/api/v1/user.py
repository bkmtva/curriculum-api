from fastapi import APIRouter, Depends, status
from src.schema import user as user_schema
from src.services.user import get_user_service, UserService
from fastapi.security import HTTPBearer
from src.utils.jwt import TokenData, ResetTokenData, get_current_active_user, logout_current_user, get_current_reset_email
from typing import Annotated
router = APIRouter(prefix="/auth", tags=["user"])

oauth2_scheme = HTTPBearer()


@router.post('/create_user', response_model=user_schema.UserRequest)
async def user_create(form_data: user_schema.UserCreate, current_user: Annotated[TokenData, Depends(get_current_active_user)],
                      user_service: UserService = Depends(get_user_service)):
    return await user_service.create_user(form_data, current_user)


@router.delete('/delete_user', status_code=status.HTTP_204_NO_CONTENT)
async def user_delete(user_id: str, current_user: Annotated[TokenData, Depends(get_current_active_user)],
                      user_service: UserService = Depends(get_user_service)):
    if current_user.is_superuser:
        
        return await user_service.delete_by_id(user_id)


@router.post("/login", response_model=user_schema.Token)
async def login(login_request: user_schema.UserLogin, user_service: UserService = Depends(get_user_service)):
    return await user_service.login_for_access_token(login_request.email, login_request.password)


@router.delete("/logout")
async def logout(current_user: Annotated[TokenData, Depends(get_current_active_user)],
                loggout_message: Annotated[TokenData, Depends(logout_current_user)],):
    return loggout_message


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def get_new_access_token(refresh_token: user_schema.RefreshToken, user_service: UserService = Depends(get_user_service)):
    return await user_service.refresh_access_token(refresh_token)


@router.get("/user-info", response_model=user_schema.UserResponse)
async def get_current_user(current_user: Annotated[TokenData, Depends(get_current_active_user)], user_service: UserService = Depends(get_user_service)):
    return await user_service.get_user_info(current_user)


@router.post('/password/reset/request/')
async def password_reset_request(password_reset_request: user_schema.PasswordResetRequest, user_service: UserService = Depends(get_user_service)) -> dict:
    return await user_service.send_email(password_reset_request)

@router.post('/password/reset/validate/')
async def password_reset_validate(token_data: Annotated[ResetTokenData, Depends(get_current_reset_email)]) -> dict:
    return {"reset_token": token_data.reset_token}

@router.post('/password/reset/new_password/')
async def password_reset_new(new_password_data: user_schema.PasswordResetNewPassword, token_data: Annotated[ResetTokenData, Depends(get_current_reset_email)], user_service: UserService = Depends(get_user_service)) -> dict:
    return await user_service.change_password(new_password_data, token_data.email)
