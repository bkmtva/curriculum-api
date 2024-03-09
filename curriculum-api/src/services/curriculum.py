from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.db.elastic import get_elastic
from src.db.redis import get_redis

from src.models.curriculum import Curriculum
from src.schema.curriculum import CurriculumResponse
from src.services.base import BaseService


class CurriculumService(BaseService):
    model = Curriculum
    schema = CurriculumResponse
    service_name = 'curriculum'


@lru_cache()
def get_curriculum_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
    db: AsyncSession = Depends(get_db)
) -> CurriculumService:
    return CurriculumService(redis, elastic, db)
