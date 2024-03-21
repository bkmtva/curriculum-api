from typing import Optional
from datetime import datetime

from orjson import orjson
from pydantic import BaseModel, EmailStr, UUID4
from typing import List
from src.schema.utils import orjson_dumps
import uuid
from typing import Optional
from src.schema.template import TemplateResponse
from src.schema.degree import DegreeResponse


class CourseCreate(BaseModel):
    title: str = ""
    course_code: str = ''
    teor: str = ''
    pr: str = ''
    cr: str = ''
    ects: str = ''
    term: str = ''
    user_id: UUID4 or str = ''

    class Config:
        from_attributes = True
        json_loads = orjson.loads
        json_dumps = orjson_dumps



class CourseResponse(CourseCreate):
    id: Optional[UUID4] = None


class CourseRequest(BaseModel):
    id: UUID4 or str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class CourseFilter(BaseModel):
    course_id: Optional[str] = None
    user_id: Optional[str] = None