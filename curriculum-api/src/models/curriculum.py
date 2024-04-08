import sqlalchemy as sa
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSON
from src.models.base import Base, UUIDMixin, CreatedUpdatedMixin
from src.models.course import Course
# from src.models.association import curriculum_course
# from src.models.user import User
class CurriculumCourse(UUIDMixin, CreatedUpdatedMixin, Base):
    __tablename__ = 'curriculum_course'

    curriculum_id = sa.Column(UUID(as_uuid=True), ForeignKey("tbl_curriculum.id", ondelete='CASCADE'), primary_key=True)
    course_id = sa.Column(UUID(as_uuid=True), ForeignKey("tbl_course.id", ondelete='CASCADE'), primary_key=True)
    semester = sa.Column(sa.Integer, nullable=False)
    order_in_semester = sa.Column(sa.Integer, nullable=False)

    curriculum = relationship("Curriculum", back_populates="courses")
    course = relationship("Course", back_populates="curriculums")
    __table_args__ = (
        UniqueConstraint('curriculum_id', 'semester', 'order_in_semester', name='_curriculum_course_uc'),
    )

class Curriculum(UUIDMixin, CreatedUpdatedMixin, Base):
    __tablename__ = "tbl_curriculum"

    title = sa.Column(sa.String(300))
    year = sa.Column(sa.String(36))
    is_main = sa.Column(sa.Boolean, default=False)

    program_id = sa.Column(UUID(as_uuid=True), ForeignKey("tbl_program.id"))
    program = relationship("Program", back_populates="curriculums")

    created_by = sa.Column(UUID(as_uuid=True), ForeignKey("tbl_user.id"))
    user = relationship("User", back_populates="curriculums")

    histories = relationship("CurriculumEditHistory", back_populates="curriculum")
    
    courses = relationship("CurriculumCourse", back_populates="curriculum", order_by=[
        CurriculumCourse.semester,
        CurriculumCourse.order_in_semester
    ])




class CurriculumEditHistory(UUIDMixin, CreatedUpdatedMixin, Base):
    __tablename__ = "tbl_cutticulum_edit_history"

    title = sa.Column(sa.String(300))
    year = sa.Column(sa.String(36))
    curriculum_versions = sa.Column(JSON, default=dict)

    edited_by = sa.Column(UUID(as_uuid=True), ForeignKey("tbl_user.id"))
    user = relationship("User", back_populates="histories")

    curriculum_id = sa.Column(UUID(as_uuid=True), ForeignKey("tbl_curriculum.id"))
    curriculum = relationship("Curriculum", back_populates="histories")
