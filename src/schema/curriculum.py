from typing import Optional, Union
from datetime import datetime

from orjson import orjson
from pydantic import BaseModel, UUID4
from typing import List
from src.schema.utils import orjson_dumps
import uuid
from typing import Optional
from src.schema.program import ProgramResponse
from src.schema.user import UserResponse
from src.schema.course import CurriculumCourseResponse

# from src.models.program import Program

class CurriculumCreate(BaseModel):
    title: str = ''
    year: str = "2024"
    is_main: bool = False
    program_id: UUID4 or str
    created_by: Optional[Union[UUID4, str]] = ''

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps



# class ProgramResponse(BaseModel):
#     id: UUID4
#     title: str = ""
#     code: str = ''
#     cipher: str = ''
#     ects: str = ''
#     degree_id: UUID4 or str
#     template_id: UUID4 or str
#
#     class Config:
#         orm_mode = True
#         from_attributes = True


class CurriculumResponse(BaseModel):
    id: UUID4
    title: str = ''
    year: str = ""
    is_main: bool
    program_id: UUID4 or str
    created_by: UUID4 or str
    program: ProgramResponse
    user: UserResponse
    courses: List[CurriculumCourseResponse]

    class Config:
        orm_mode = True
        from_attributes = True
        json_loads = orjson.loads
        json_dumps = orjson_dumps



class CurriculumSchema(CurriculumResponse):
    program_title: str = ''
    semester_count: int = 8
    degree_name: str = ''


class CurriculumRequest(BaseModel):
    id: UUID4


class CurriculumFilter(BaseModel):
    year: Optional[str] = '2024'
    program_id: Optional[str] = None
