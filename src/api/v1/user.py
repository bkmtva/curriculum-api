from fastapi import APIRouter, Depends, status, UploadFile, File, Body, Form, HTTPException
from src.schema import user as user_schema
from src.services.user import get_user_service, UserService
from fastapi.security import HTTPBearer
from src.utils.jwt import TokenData, ResetTokenData, get_current_active_user, logout_current_user, get_current_reset_email
from typing import Annotated, Optional, Union, List
from pydantic import BaseModel, Json
router = APIRouter(prefix="/user", tags=["user"])
from dataclasses import dataclass
oauth2_scheme = HTTPBearer()


@router.get('', response_model=List[user_schema.UserDetailSchema])
async def user_list(
        current_user: Annotated[TokenData, Depends(get_current_active_user)],
        user_service: UserService = Depends(get_user_service)
):
    return await user_service.get_all_with_pagination()

@router.post('', response_model=user_schema.UserRequest)
async def user_create(
        form_data: Annotated[Json[user_schema.UserCreate], Form]= user_schema.UserCreate().json(),
        profile_image: Optional[Union[UploadFile, str]] = '',
        current_user: TokenData = Depends(get_current_active_user),
        user_service: UserService = Depends(get_user_service)
):
    return await user_service.create_user(form_data=form_data, token_data=current_user, file=profile_image)

@router.get('/{user_id}', response_model=user_schema.UserDetailSchema)
async def user_get(
        user_id: str,
        current_user: TokenData = Depends(get_current_active_user),
        user_service: UserService = Depends(get_user_service)
):
    return await user_service.get_by_id(user_id)


@router.put('/{user_id}', response_model=user_schema.UserRequest)
async def user_update(
        user_id: str,
        form_data: Annotated[Json[user_schema.UserUpdate], Form]= user_schema.UserUpdate().json(),
        profile_image: Optional[Union[UploadFile, str]] = '',
        current_user: TokenData = Depends(get_current_active_user),
        user_service: UserService = Depends(get_user_service)
):
    return await user_service.update_object(obj_id=user_id, current_user=current_user, obj_sch=form_data, file=profile_image)

@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def user_delete(
        user_id: str,
        current_user: Annotated[TokenData, Depends(get_current_active_user)],
        user_service: UserService = Depends(get_user_service)
):
    if current_user.is_superuser:
        return await user_service.delete_by_id(user_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No access",
            headers={"WWW-Authenticate": "Bearer"}
        )