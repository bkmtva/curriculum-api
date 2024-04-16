from functools import lru_cache
import sqlalchemy as sa
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List
from src.db.database import get_db
from src.db.elastic import get_elastic
from src.db.redis import get_redis
from sqlalchemy.orm import class_mapper, RelationshipProperty, selectinload, joinedload, defer, undefer, load_only
from src.models.curriculum import Curriculum
from src.models.course import Course
from src.models.program import Program
from src.models.user import User
from src.models.curriculum import CurriculumCourse
from src.schema.curriculum import CurriculumResponse, CurriculumSchema
from src.services.base import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import select, func, and_, desc, delete, update
from fastapi import HTTPException, status
import json

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
                        selectinload(Curriculum.courses).options(selectinload(CurriculumCourse.course),),
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

            return main_curr

        async def get_all(self, year: str = "2024", program_id: str = None, user_id: str = None):
            query = (
                select(self.model)
                .filter(self.model.year == year, self.model.created_by == user_id)
                .options(
                    selectinload(Curriculum.program).options(selectinload(Program.template)),
                    selectinload(Curriculum.courses).options(selectinload(CurriculumCourse.course)),
                    selectinload(Curriculum.user).options(defer(User.password)),

                )
            )
            if program_id:
                query = query.filter(self.model.program_id == program_id)
            curriculums_execute = await self.db.execute(query)
            curriculums_result = curriculums_execute.scalars().all()
            if not curriculums_result:
                raise HTTPException(status_code=404, detail=f"No curriculums found for the year {year} and program")

            curriculums = [curriculum.__dict__ for curriculum in curriculums_result]
            for curriculum in curriculums:
                curriculum['program_title'] = curriculum.get("program", {}).title
                curriculum['semester_count'] = curriculum.get("program", {}).template.semester_count
                # curriculums.pop("program")

            return curriculums

        async def get_curriculum_by_id(self, curriculum_id: str = None, user_id: str = None):
            query = (
                select(self.model)
                .filter(self.model.id == curriculum_id, self.model.created_by == user_id)
                .options(
                    selectinload(Curriculum.program).options(selectinload(Program.template), selectinload(Program.degree)),
                    selectinload(Curriculum.courses).options(selectinload(CurriculumCourse.course)),
                    selectinload(Curriculum.user).options(defer(User.password)),

                )
            )

            curriculum_execute = await self.db.execute(query)
            curriculum_result = curriculum_execute.scalar()
            if not curriculum_result:
                raise HTTPException(status_code=404, detail=f"No curriculum found")

            curriculum = curriculum_result.__dict__

            curriculum['program_title'] = curriculum.get("program", {}).title
            # curriculum['program_id'] = curriculum.get("program", {}).id
            curriculum['semester_count'] = curriculum.get("program", {}).template.semester_count
            curriculum['degree_name'] = curriculum.get("program", {}).degree.name
            curriculum.pop('program')
                # curriculums.pop("program")

            return curriculum


        async def get_curriculum(self, curriculum_id: str = None, user_id: str = None):
            query = (
                select(self.model)
                .filter(self.model.id == curriculum_id, self.model.created_by == user_id)
                .options(
                    selectinload(Curriculum.program).options(selectinload(Program.template), selectinload(Program.degree)),
                    selectinload(Curriculum.courses).options(selectinload(CurriculumCourse.course)),
                    selectinload(Curriculum.user).options(defer(User.password)),

                )
            )

            curriculum_execute = await self.db.execute(query)
            curriculum_result = curriculum_execute.scalar()
            curriculum = CurriculumSchema.from_orm(curriculum_result)
            if not curriculum_result:
                raise HTTPException(status_code=404, detail=f"No curriculum found")

            curriculum.program_title = curriculum.program.title
            curriculum.semester_count = curriculum.program.template.semester_count
            curriculum.degree_name = curriculum.program.degree.name

            return curriculum

        async def todict(self, obj, classkey=None):
            # if isinstance(obj, dict):
            #     data = {}
            #     for (k, v) in obj.items():
            #         data[k] = todict(v, classkey)
            #     return data
            if hasattr(obj, "_ast"):
                return todict(obj._ast())
            elif hasattr(obj, "__iter__") and not isinstance(obj, str):
                return [todict(v, classkey) for v in obj]
            elif hasattr(obj, "__dict__"):
                data = dict([(key, todict(value, classkey))
                             for key, value in obj.__dict__.items()
                             if not callable(value) and not key.startswith('_')])
                if classkey is not None and hasattr(obj, "__class__"):
                    data[classkey] = obj.__class__.__name__
                return data
            else:
                return obj

        async def get_all_curriculums_by_program(self, year: str = "2024", program_id: str = None, user_id: str = None):
            query = (
                select(self.model)
                .filter(self.model.year == year, self.model.created_by == user_id)
                .options(
                    selectinload(Curriculum.program).options(undefer(Program.title), selectinload(Program.degree)),
                    selectinload(Curriculum.user).options(load_only("first_name", "last_name")),

                )
            )
            if program_id:
                query = query.filter(self.model.program_id == program_id)
            curriculums_execute = await self.db.execute(query)
            curriculums_result = curriculums_execute.scalars().all()
            if not curriculums_result:
                raise HTTPException(status_code=404, detail=f"No curriculums found for the year {year} and program")

            curriculums = [curriculum.__dict__ for curriculum in curriculums_result]
            program_title = ''
            degree_name = ''
            for curriculum in curriculums:
                program_title = curriculum.get("program", {}).title
                degree_name = curriculum.get("program", {}).degree.name
                curriculum['program_title'] = program_title
                curriculum['degree_name'] = degree_name
                curriculum.pop("program")
            program = {'program_title': program_title, 'degree_name': degree_name}
            all_currilims = {'curriculums': curriculums, 'program': program}

            return all_currilims

        async def update_curriculum(self, courses: List[dict] = None, curriculum_id: str = None,  user_id: str = None):
            curriculum = await self.db.execute(
                select(self.model)
                .options(selectinload(Curriculum.courses)
                         .options(selectinload(CurriculumCourse.course)),)
                .where(self.model.id == curriculum_id)
            )
            curriculum = curriculum.scalars().first()
            if not curriculum:
                raise HTTPException(status_code=404, detail="Curriculum not found")

            await self.db.execute(delete(CurriculumCourse).where(CurriculumCourse.curriculum_id == curriculum.id))

            for course_info in courses:
                course_id = course_info.get("course_id")
                semester = course_info.get("semester")
                order_in_semester = course_info.get("order_in_semester")

                if not course_id:
                    raise HTTPException(status_code=400, detail="Missing course_id")
                if not semester:
                    raise HTTPException(status_code=400, detail="Missing semester")
                if not order_in_semester:
                    raise HTTPException(status_code=400, detail="Missing order_in_semester")
                course = await self.db.execute(select(Course).filter(Course.id == course_info.get("course_id")))
                course = course.scalars().first()

                if not course:
                    raise HTTPException(status_code=404, detail=f"Course with ID {course_id} not found")
                curriculum_course = CurriculumCourse(
                    curriculum_id=curriculum_id,
                    course_id=course_id,
                    semester=semester,
                    order_in_semester=order_in_semester
                )

                # Add the new instance to the curriculum's courses
                curriculum.courses.append(curriculum_course)

            # Commit changes
            await self.db.commit()
            return {"message": "Curriculum courses updated successfully"}

        async def set_as_main(self, curriculum_id: str):

            result = await self.db.execute(select(self.model).filter(self.model.id == curriculum_id))
            curriculum = result.scalars().first()
            if not curriculum:
                raise HTTPException(status_code=404, detail="Curriculum not found")

            # Update the target curriculum to be main
            curriculum.is_main = True

            # Reset other curriculums in the same program, user, and year to False
            await self.db.execute(
                update(Curriculum).filter(
                    Curriculum.program_id == curriculum.program_id,
                    Curriculum.created_by == curriculum.created_by,
                    Curriculum.year == curriculum.year,
                    Curriculum.id != curriculum_id
                ).values(is_main=False)
            )

            await self.db.commit()
            return {"message": f"Curriculum {curriculum.title} set as main successfully"}


@lru_cache()
def get_curriculum_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
    db: AsyncSession = Depends(get_db)
) -> CurriculumService:
    return CurriculumService(redis, elastic, db)
