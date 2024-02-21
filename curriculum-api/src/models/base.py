from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class UUIDMixin(object):
    id = Column(UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid(), unique=True)
