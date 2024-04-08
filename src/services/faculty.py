from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.db.elastic import get_elastic
from src.db.redis import get_redis

from src.models.faculty import Faculty
from src.schema.faculty import FacultyResponse
from src.services.base import BaseService


class FacultyService(BaseService):
    model = Faculty
    schema = FacultyResponse
    service_name = 'faculty'


@lru_cache()
def get_faculty_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
    db: AsyncSession = Depends(get_db)
) -> FacultyService:
    return FacultyService(redis, elastic, db)
