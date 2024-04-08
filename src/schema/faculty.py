from typing import Optional
from datetime import datetime

from orjson import orjson
from pydantic import BaseModel, EmailStr, UUID4
from typing import List
from src.schema.utils import orjson_dumps
import uuid
from typing import Optional


class FacultyCreate(BaseModel):
    title: str = ""
    logo: str or None = ''

    class Config:
        from_attributes = True
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class FacultyResponse(FacultyCreate):
    id: UUID4


class FacultyRequest(BaseModel):
    id: UUID4

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class FacultyFilter(BaseModel):
    year: str = ""
    is_main: bool = False

