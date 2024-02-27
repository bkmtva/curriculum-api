from typing import Optional
from datetime import datetime

from orjson import orjson
from pydantic import BaseModel, UUID4
from typing import List
from src.schema.utils import orjson_dumps
import uuid

class UserRequest(BaseModel):
    email: str
    first_name: str or None = None
    is_active: bool = True
    is_superuser: bool = False
    program_id: UUID4 = uuid.UUID('5e1fb87d-4db4-4c06-ace3-b3a4d1302536')

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps

class UserCreate(UserRequest):
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        

class UserInDB(UserRequest):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: str or None = None
