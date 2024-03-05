from orjson import orjson
from pydantic import BaseModel

from src.schema.utils import orjson_dumps


class FacultyRequest(BaseModel):
    title: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class FacultySchema(FacultyRequest):
    id: str
