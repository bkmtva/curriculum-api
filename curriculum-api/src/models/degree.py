import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base, UUIDMixin, CreatedUpdatedMixin
from sqlalchemy.dialects.postgresql import UUID
from src.models.program import Program


class Degree(UUIDMixin, Base):
    __tablename__ = "tbl_degree"

    name = sa.Column(sa.String(300))

    faculty_id = sa.Column(UUID(as_uuid=True), ForeignKey("tbl_faculty.id"))
    faculty = relationship("Faculty", back_populates="degrees")

    programs = relationship("Program", back_populates="degree")
