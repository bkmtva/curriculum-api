from orjson import orjson
from pydantic import BaseModel

from src.schema.utils import orjson_dumps


class ProgramRequest(BaseModel):
    title: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class ProgramSchema(ProgramRequest):
    id: str
