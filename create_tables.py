from sqlalchemy import create_engine
import os
from logging import config as logging_config
from src.core.logger import LOGGING

from src.models.base import Base
from src.models.user import User
from src.models.faculty import Faculty
from src.models.degree import Degree
from src.models.program import Program
from src.models.template import Template
from src.models.curriculum import Curriculum, CurriculumCourse
from src.models.course import Course, Subcourse, Prerequisite


logging_config.dictConfig(LOGGING)

C_DATABASE_URL = os.getenv('DATABASE_URL', os.getenv('SYNC_DATABASE_URL'))

db_engine = create_engine(C_DATABASE_URL, echo=True, pool_pre_ping=True)
Base.metadata.create_all(bind=db_engine)


