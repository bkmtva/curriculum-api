from typing import Optional
from datetime import datetime

from orjson import orjson
from pydantic import BaseModel, EmailStr, UUID4
from typing import List
from src.schema.utils import orjson_dumps
import uuid
from typing import Optional

class UserRequest(BaseModel):
    first_name: str or None = ""
    last_name: str or None = ""
    email: str = ""
    profile_image: Optional[str] or None = ''
    datetime_created: datetime = datetime.utcnow()
    last_login_at: datetime or None = datetime.utcnow()
    is_active: bool = True
    is_superuser: bool = False
    faculty_id: UUID4 or str = uuid.UUID('5e1fb87d-4db4-4c06-ace3-b3a4d1302536')


    class Config:
        from_attributes = True


class UserResponse(UserRequest):
    id: UUID4

class UserCreate(UserRequest):
    password: str =""


class UserUpdate(UserRequest):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    profile_image: Optional[str] or Optional[None] = None
    datetime_created: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    faculty_id: Optional[str] = None
    password: Optional[str] = None
    old_password: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        

class UserInDB(UserResponse):
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    message: str
    token_type: str = "bearer"

class RefreshToken(BaseModel):
    refresh_token: str

class RefreshedToken(BaseModel):
    access_token: str
    message: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: str | None = None
    is_superuser: bool = False
    disabled: bool | None = None
    email: str | None = None
    faculty_id: str | None = None

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetToken(BaseModel):
    reset_token: str

class PasswordResetNewPassword(BaseModel):
    new_password: str
    repeat_new_password: str