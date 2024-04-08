from typing import Optional
from datetime import datetime

from orjson import orjson
from pydantic import BaseModel, EmailStr, UUID4
from typing import List
from src.schema.utils import orjson_dumps
import uuid
from typing import Optional


class DegreeCreate(BaseModel):
    name: str = ""
    faculty_id: UUID4 or str

    class Config:
        from_attributes = True
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class DegreeResponse(DegreeCreate):
    id: UUID4


class DegreeRequest(BaseModel):
    id: UUID4

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps

class DegreeFilter(BaseModel):
    faculty_id: Optional[UUID4] = None

