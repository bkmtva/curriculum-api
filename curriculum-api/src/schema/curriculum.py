from typing import Optional
from datetime import datetime

from orjson import orjson
from pydantic import BaseModel, UUID4
from typing import List
from src.schema.utils import orjson_dumps
import uuid
from typing import Optional
from src.schema.program import ProgramResponse
from src.schema.user import UserResponse
from src.schema.course import CourseResponse

# from src.models.program import Program

class CurriculumCreate(BaseModel):
    title: str = ''
    year: str = ""
    is_main: bool
    program_id: UUID4 or str
    created_by: UUID4 or str

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
    courses: List[CourseResponse]

    class Config:
        orm_mode = True
        from_attributes = True
        json_loads = orjson.loads
        json_dumps = orjson_dumps

    @classmethod
    def from_orm(cls, curriculum_orm):
        program_response = ProgramResponse.from_orm(curriculum_orm.program)
        user_response = UserResponse.from_orm(curriculum_orm.user)
        courses_response = [CourseResponse.from_orm(course) for course in curriculum_orm.courses]

        return cls(
            id=curriculum_orm.id,
            title=curriculum_orm.title,
            year=curriculum_orm.year,
            is_main=curriculum_orm.is_main,
            program_id=curriculum_orm.program_id,
            created_by=curriculum_orm.created_by,
            program=program_response,
            user=user_response,
            courses=courses_response,
        )


class CurriculumRequest(BaseModel):
    id: UUID4


class CurriculumFilter(BaseModel):
    year: Optional[str] = '2024'
    program_id: Optional[str] = None
