from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.db.elastic import get_elastic
from src.db.redis import get_redis

from src.models.program import Program
from src.models.curriculum import Curriculum
from src.schema.program import ProgramResponse
from src.services.base import BaseService
from sqlalchemy.future import select
from sqlalchemy import select, func, and_, desc
import sqlalchemy as sa
from sqlalchemy.orm import class_mapper, RelationshipProperty, selectinload, joinedload

class ProgramService(BaseService):
    model = Program
    schema = ProgramResponse
    service_name = 'program'

    async def get_all_main(self, year: str = "2024"):
        subquery = (
            select(Curriculum.program_id, func.last_value(Curriculum.id).over(
                partition_by=Curriculum.program_id,
                order_by=desc(Curriculum.id)
            ).label("latest_curriculum_id")
            )
            .distinct(Curriculum.program_id)
            .alias("subquery")
        )

        main_curriculums = (
            await self.db.execute(
                select(Curriculum)
                .join(subquery, and_(Curriculum.program_id == subquery.c.program_id,
                      Curriculum.id == subquery.c.latest_curriculum_id)
                      ).options(
                        selectinload(Curriculum.program),)
            )
        ).scalars().all()
        main_programs = [curriculum.program for curriculum in main_curriculums]
        if not main_curriculums:
            raise HTTPException(status_code=404, detail=f"No main curriculums found for the year {year}")
        return {"main_programs": main_programs,}



@lru_cache()
def get_program_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
    db: AsyncSession = Depends(get_db)
) -> ProgramService:
    return ProgramService(redis, elastic, db)
