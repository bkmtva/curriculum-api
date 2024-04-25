import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from src.models.base import Base, UUIDMixin, CreatedUpdatedMixin
# from src.models.user import User
# from src.models.association import curriculum_course
# from src.models.curriculum import Curriculum

class Course(UUIDMixin, CreatedUpdatedMixin,  Base):
    """
        Represents a course offered within a curriculum.
    """
    __tablename__ = "tbl_course"

    title = sa.Column(sa.String(300))
    title_kz = sa.Column(sa.String(300))
    title_ru = sa.Column(sa.String(300))
    course_code = sa.Column(sa.String(300))
    teor = sa.Column(sa.Integer, nullable=True)
    pr = sa.Column(sa.String(300), nullable=True)
    cr = sa.Column(sa.Integer, nullable=True)
    ects = sa.Column(sa.Integer, nullable=True)
    term = sa.Column(sa.String(300), nullable=True)

    user_id = sa.Column(UUID(as_uuid=True), ForeignKey("tbl_user.id"))
    user = relationship("User", back_populates="courses")

    curriculums = relationship("CurriculumCourse", back_populates="course", cascade="all, delete-orphan")
    prerequisites = relationship("Course",
                                 secondary="tbl_prerequisite",
                                 primaryjoin="Course.id==Prerequisite.child_id",
                                 secondaryjoin="Course.id==Prerequisite.prerequisit_id",
                                 backref="required_by")
    subcourses = relationship("Course",
                              secondary="tbl_subcourse",
                              primaryjoin="Course.id==Subcourse.parent_course_id",
                              secondaryjoin="Course.id==Subcourse.subcourse_id",
                              backref="parent_courses")


class Prerequisite(UUIDMixin, Base):
    """
        Represents a prerequisite relationship between courses.
    """
    __tablename__ = 'tbl_prerequisite'

    child_id = sa.Column(UUID(as_uuid=True), ForeignKey("tbl_course.id", ondelete='CASCADE'), primary_key=True)
    prerequisit_id = sa.Column(UUID(as_uuid=True), ForeignKey("tbl_course.id", ondelete='CASCADE'), primary_key=True)


    __table_args__ = (
        sa.UniqueConstraint('child_id', 'prerequisit_id', name='_prerequisite_course_uc'),
    )


class Subcourse(UUIDMixin, Base):
    """
        Represents a subcourse relationship within a course.
    """
    __tablename__ = 'tbl_subcourse'

    parent_course_id = sa.Column(UUID(as_uuid=True), ForeignKey("tbl_course.id", ondelete='CASCADE'), primary_key=True)
    subcourse_id = sa.Column(UUID(as_uuid=True), ForeignKey("tbl_course.id", ondelete='CASCADE'), primary_key=True)



    __table_args__ = (
        sa.UniqueConstraint('parent_course_id', 'subcourse_id', name='_subcourse_uc'),
    )