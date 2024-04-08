from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.db.elastic import get_elastic
from src.db.redis import get_redis

from src.models.course import Course
from src.schema.course import CourseResponse
from src.services.base import BaseService


class CourseService(BaseService):
    model = Course
    schema = CourseResponse
    service_name = 'course'


@lru_cache()
def get_course_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
    db: AsyncSession = Depends(get_db)
) -> CourseService:
    return CourseService(redis, elastic, db)
