from functools import lru_cache
import sqlalchemy as sa
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.db.elastic import get_elastic
from src.db.redis import get_redis
from sqlalchemy.orm import class_mapper, RelationshipProperty, selectinload, joinedload
from src.models.curriculum import Curriculum
from src.models.course import Course
from src.models.program import Program
from src.models.curriculum import CurriculumCourse as curriculum_course
from src.schema.curriculum import CurriculumResponse
from src.services.base import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import select, func, and_, desc
from fastapi import HTTPException, status


class CurriculumService(BaseService):
        model = Curriculum
        schema = CurriculumResponse
        service_name = 'curriculum'

        async def get_all_main(self, year: str = "2024", program_id: str = ""):
            subquery = (
                select(self.model.program_id, func.last_value(self.model.id).over(
                    partition_by=self.model.program_id,
                    order_by=desc(self.model.id)
                ).label("latest_curriculum_id")
                       )
                .filter(self.model.is_main == True)
                .filter(self.model.year == year)
                .filter(self.model.program_id == program_id)
                .distinct(self.model.program_id)
                .alias("subquery")
            )

            main_curriculums = (
                await self.db.execute(
                    select(self.model)
                    .join(subquery, and_(self.model.program_id == subquery.c.program_id,
                                         self.model.id == subquery.c.latest_curriculum_id))
                    .options(
                        selectinload(Curriculum.courses).options(selectinload(curriculum_course.course),),
                        selectinload(Curriculum.program).options(selectinload(Program.template),
                                 ),

                    )
                )
            ).scalars().all()


            if not main_curriculums:
                raise HTTPException(status_code=404, detail=f"No main curriculums found for the year {year}")

            main_curr = main_curriculums[0].__dict__
            main_curr['program_title'] = main_curr.get("program", {}).title
            main_curr['semester_count'] = main_curr.get("program", {}).template.semester_count
            main_curr['courses'] = main_curr.get("courses", {})
            main_curr.pop("program")
            program_title = main_curr.pop("program_title")
            program_title = main_curr.pop("program_title")
            ordered_data = {"program_title": program_title}
            ordered_data.update(data)

            return main_curr


        async def get_all(self, year: str = "2024", program_id: str = ""):
            subquery = (
                select(self.model.program_id)
                .filter(self.model.year == year)
                .filter(self.model.program_id == program_id)
                .alias("subquery")
            )

            main_curriculums = (
                await self.db.execute(
                    select(self.model)
                    .join(subquery)
                    .options(
                        selectinload(Curriculum.courses)
                        .options(selectinload(curriculum_course.course)
                                 ),
                    )
                )
            ).scalars().all()
            if not main_curriculums:
                raise HTTPException(status_code=404, detail=f"No main curriculums found for the year {year}")
            return {"main_currs": [curriculum.__dict__ for curriculum in main_curriculums]}




@lru_cache()
def get_curriculum_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
    db: AsyncSession = Depends(get_db)
) -> CurriculumService:
    return CurriculumService(redis, elastic, db)
