from sqlalchemy import create_engine
from src.models.base import Base
from src.models.user import User
from src.models.faculty import Faculty
from src.models.program import Program
import os
from logging import config as logging_config

from src.core.logger import LOGGING

logging_config.dictConfig(LOGGING)

C_DATABASE_URL = os.getenv('DATABASE_URL', "postgresql://postgres:bkm@localhost:5432/test_cur_db")

db_engine = create_engine(C_DATABASE_URL, echo=True, pool_pre_ping=True)
Base.metadata.create_all(bind=db_engine)


