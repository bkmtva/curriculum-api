from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.db.elastic import get_elastic
from src.db.redis import get_redis

from src.models.template import Template
from src.schema.template import TemplateResponse
from src.services.base import BaseService


class TemplateService(BaseService):
    model = Template
    schema = TemplateResponse
    service_name = 'template'


@lru_cache()
def get_template_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
    db: AsyncSession = Depends(get_db)
) -> TemplateService:
    return TemplateService(redis, elastic, db)
