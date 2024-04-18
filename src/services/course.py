import logging
from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.db.database import get_db
from src.db.elastic import get_elastic
from src.db.redis import get_redis

from src.models.course import Course, Prerequisite, Subcourse
from src.schema.course import CourseResponse, CourseInfo, CourseDetailSchema
from src.services.base import BaseService
from sqlalchemy.future import select
logger = logging.getLogger(__name__)


class CourseService(BaseService):
    model = Course
    schema = CourseResponse
    detail_schema = CourseDetailSchema
    service_name = 'course'
    search_fields = ['title', 'course_code']
    relationship_options = {
        'pre_ids': {
            'model': Course,
            'schema': CourseInfo,
            'field': 'prerequisites'
        },
        'sub_ids': {
            'model': Course,
            'schema': CourseInfo,
            'field': 'subcourses'
        }
    }

    async def _get_object_from_db(self, obj_id):
        return (await self.db.execute(select(Course).options(
            selectinload(Course.prerequisites),
            selectinload(Course.subcourses),
        ).filter_by(id=obj_id))).scalar()

    # async def create_object(self, obj_sch):
    #     others = {}
    #     obj_dict = obj_sch.dict()
    #     for key, value in self.relationship_options.items():
    #         others[value['field']] = await self._set_obj_ids(obj_dict.pop(key), value['model'])
    #     db_obj = self.model(**obj_dict)
    #     for key, value in others.items():
    #         setattr(db_obj, key, value)
    #     self.db.add(db_obj)
    #     await self.db_commit()
    #     await self.db.refresh(db_obj)
    #
    #     return db_obj




@lru_cache()
def get_course_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
    db: AsyncSession = Depends(get_db)
) -> CourseService:
    return CourseService(redis, elastic, db)
