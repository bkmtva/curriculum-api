from typing import Optional
from datetime import datetime

from orjson import orjson
from pydantic import BaseModel, EmailStr, UUID4
from typing import List
from src.schema.utils import orjson_dumps
import uuid
from typing import Optional, Union


class DegreeCreate(BaseModel):
    name: str = ""
    faculty_id: Optional[Union[UUID4, str]] = ''

    class Config:
        from_attributes = True
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class DegreeResponse(DegreeCreate):
    id: Optional[UUID4] or Optional[str]


class DegreeRequest(BaseModel):
    id: UUID4

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps

class DegreeFilter(BaseModel):
    faculty_id: Optional[UUID4] = None

