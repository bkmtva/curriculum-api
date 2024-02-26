from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.db.elastic import get_elastic
from src.db.redis import get_redis

from src.models.faculty import Program
from src.schema.program import ProgramSchema
from src.services.base import BaseService


class ProgramService(BaseService):
    model = Program
    schema = ProgramSchema
    service_name = 'program'


@lru_cache()
def get_program_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
    db: AsyncSession = Depends(get_db)
) -> ProgramService:
    return ProgramService(redis, elastic, db)
