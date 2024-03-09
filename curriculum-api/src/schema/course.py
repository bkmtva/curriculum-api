from typing import Optional
from datetime import datetime

from orjson import orjson
from pydantic import BaseModel, UUID4
from typing import List
from src.schema.utils import orjson_dumps
import uuid
from typing import Optional
# from src.schema.program import ProgramResponse
# from src.schema.user import UserResponse
# from src.schema.course import CourseResponse

# from src.models.program import Program

class CourseCreate(BaseModel):
    title: str = ''
    year: str = ""
    is_main: bool
    program_id: UUID4 or str
    created_by: UUID4 or str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class CourseResponse(BaseModel):
    id: UUID4
    course_code: str = ''
    teor: str = ""
    pr: str = ''
    cr: str = ''
    ects: str = ''
    term: str = ''

    class Config:
        orm_mode = True
        from_attributes = True
        json_loads = orjson.loads
        json_dumps = orjson_dumps



class CourseRequest(BaseModel):
    id: UUID4


class CourseFilter(BaseModel):
    year: str = ''
    is_main: bool = False