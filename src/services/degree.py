from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.db.elastic import get_elastic
from src.db.redis import get_redis

from src.models.degree import Degree
from src.schema.degree import DegreeResponse
from src.services.base import BaseService


class DegreeService(BaseService):
    model = Degree
    schema = DegreeResponse
    service_name = 'degree'


@lru_cache()
def get_degree_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
    db: AsyncSession = Depends(get_db)
) -> DegreeService:
    return DegreeService(redis, elastic, db)
