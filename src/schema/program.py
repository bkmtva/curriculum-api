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


class ProgramCreate(BaseModel):
    title: str = ""
    code: str = ''
    cipher: str = ''
    ects: str = ''
    degree_id: UUID4 or str
    template_id: UUID4 or str

    class Config:
        from_attributes = True
        json_loads = orjson.loads
        json_dumps = orjson_dumps



class ProgramResponse(ProgramCreate):
    template: TemplateResponse
    degree: DegreeResponse
    id: UUID4



class ProgramRequest(BaseModel):
    id: UUID4

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps

class ProgramFilter(BaseModel):
    degree_id: Optional[UUID4] = None