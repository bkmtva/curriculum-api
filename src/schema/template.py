from typing import Optional
from datetime import datetime

from orjson import orjson
from pydantic import BaseModel, EmailStr, UUID4
from typing import List
from src.schema.utils import orjson_dumps
import uuid
from typing import Optional


class TemplateCreate(BaseModel):
    title: str = ""
    semester_count: int = 8

    class Config:
        from_attributes = True
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class TemplateResponse(TemplateCreate):
    id: UUID4


class TemplateRequest(BaseModel):
    id: UUID4

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class TemplateFilter(BaseModel):
    year: str = ''
    is_main: bool = False

