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

    @classmethod
    def from_orm(cls, program_orm):
        template_response = TemplateResponse.from_orm(program_orm.template)
        degree_response = DegreeResponse.from_orm(program_orm.degree)

        return cls(
            id=program_orm.id,
            title=program_orm.title,
            code=program_orm.code,
            cipher=program_orm.cipher,
            ects=program_orm.ects,
            degree_id=program_orm.degree_id,
            template_id=program_orm.template_id,
            template=template_response,
            degree=degree_response
        )


class ProgramRequest(BaseModel):
    id: UUID4

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps

class ProgramFilter(BaseModel):
    degree_id: Optional[UUID4] = None