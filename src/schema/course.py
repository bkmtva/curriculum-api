from typing import Optional, Union
from datetime import datetime

from orjson import orjson
from pydantic import BaseModel, EmailStr, UUID4
from typing import List
from src.schema.utils import orjson_dumps
import uuid
from src.schema.template import TemplateResponse
from src.schema.degree import DegreeResponse
# from src.schema.curriculum import CurriculumResponse
class CourseInfo(BaseModel):
    title: str = ""
    title_kz: str = ""
    title_ru: str = ""
    course_code: str = ''
    teor: Optional[int] = None
    pr: str = ''
    cr: Optional[int] = None
    ects: Optional[int] = None
    term: Optional[str] = None
    user_id: Optional[Union[UUID4, str]] = ''


class CourseCreate(CourseInfo):
    sub_ids: Optional[List[str]] = None
    pre_ids: Optional[List[str]] = None

    class Config:
        from_attributes = True
        json_loads = orjson.loads
        json_dumps = orjson_dumps



class CourseResponse(CourseInfo):
    id: Optional[UUID4] or Optional[str] or Optional[None] = None
    class Config:
        from_attributes = True

class CourseDetailSchema(CourseResponse):
    prerequisites: Optional[List[CourseResponse]] = None
    subcourses: Optional[List[CourseResponse]] = None

    class Config:
        from_attributes = True
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class CurriculumCourseResponse(BaseModel):
    order_in_semester: int = 1
    semester: int = 1
    curriculum_id: Optional[Union[UUID4, str]] = ''
    course_id: Optional[Union[UUID4, str]] = ''
    user_id: Optional[Union[UUID4, str]] = ''
    course: CourseDetailSchema

    class Config:
        orm_mode = True
        from_attributes = True
        json_loads = orjson.loads
        json_dumps = orjson_dumps



class CourseRequest(BaseModel):
    id: UUID4 or str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class CourseFilter(BaseModel):
    course_id: Optional[str] = None
    user_id: Optional[str] = None



class CourseUpdate(BaseModel):
    title: Optional[str] = None
    title_kz: Optional[str] = None
    title_ru: Optional[str] = None
    course_code: Optional[str] = None
    teor: Optional[int] = None
    pr: Optional[str] = None
    cr: Optional[int] = None
    ects: Optional[int] = None
    term: Optional[str] = None
    user_id: Optional[str] = None
    sub_ids: Optional[List[str]] = []
    pre_ids: Optional[List[str]] = []

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        use_enum_values = True
        from_attributes = True