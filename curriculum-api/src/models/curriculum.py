import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSON
from src.models.base import Base, UUIDMixin
from src.models.course import Course
from src.models.association import curriculum_course
# from src.models.user import User


class Curriculum(UUIDMixin, Base):
    __tablename__ = "tbl_curriculum"

    title = sa.Column(sa.String(300))
    year = sa.Column(sa.String(36))

    program_id = sa.Column(UUID(as_uuid=True), ForeignKey("tbl_program.id"))
    program = relationship("Program", back_populates="curriculums")

    created_by = sa.Column(UUID(as_uuid=True), ForeignKey("tbl_user.id"))
    user = relationship("User", back_populates="curriculums")

    histories = relationship("CurriculumEditHistory", back_populates="curriculum")
    
    courses = relationship("Course", secondary=curriculum_course, back_populates="curriculums")


class CurriculumEditHistory(UUIDMixin, Base):
    __tablename__ = "tbl_cutticulum_edit_history"

    title = sa.Column(sa.String(300))
    year = sa.Column(sa.String(36))
    curriculum_versions = sa.Column(JSON, default=dict)

    edited_by = sa.Column(UUID(as_uuid=True), ForeignKey("tbl_user.id"))
    user = relationship("User", back_populates="histories")

    curriculum_id = sa.Column(UUID(as_uuid=True), ForeignKey("tbl_curriculum.id"))
    curriculum = relationship("Curriculum", back_populates="histories")
