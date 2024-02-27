import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base, UUIDMixin
from sqlalchemy.dialects.postgresql import UUID
from src.models.faculty import Faculty


class Program(UUIDMixin, Base):
    __tablename__ = "tbl_program"

    title = sa.Column(sa.String(300))
    code = sa.Column(sa.String(36))
    cipher = sa.Column(sa.String(36))
    level = sa.Column(sa.String(36))

    users = relationship("User", back_populates="program")

    faculty_id = sa.Column(UUID(as_uuid=True), ForeignKey('tbl_faculty.id'))
    faculty = relationship("Faculty", back_populates="programs")
