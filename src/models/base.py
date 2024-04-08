from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy import Column, String, func, DateTime

Base = declarative_base()


class UUIDMixin(object):
    id = Column(UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid(), unique=True)


class CreatedUpdatedMixin(object):
    datetime_updated = Column(DateTime, onupdate=func.now())
    datetime_created = Column(DateTime, default=func.now())
