from typing import Optional
from datetime import datetime

from orjson import orjson
from pydantic import BaseModel, EmailStr, UUID4
from typing import List
from src.schema.utils import orjson_dumps
import uuid
from typing import Optional

class UserRequest(BaseModel):
    id: UUID4 or str
    first_name: str = ""
    last_name: str or None = ""
    email: str = ""
    profile_image: Optional[str] or None = ''
    created_at: datetime = datetime.utcnow()
    last_login_at: datetime or None = datetime.utcnow()
    is_active: bool = True
    is_superuser: bool = False
    faculty_id: UUID4 or str = uuid.UUID('5e1fb87d-4db4-4c06-ace3-b3a4d1302536')


    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps

class UserResponse(UserRequest):
    id: UUID4

class UserCreate(UserRequest):
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        

class UserInDB(UserRequest):
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    message: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: str or None = None
