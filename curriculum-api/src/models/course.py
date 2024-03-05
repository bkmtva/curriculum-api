import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from src.models.base import Base, UUIDMixin
# from src.models.user import User
from src.models.association import curriculum_course
# from src.models.curriculum import Curriculum

class Course(UUIDMixin, Base):
    __tablename__ = "tbl_course"

    title = sa.Column(sa.String(300))
    course_code = sa.Column(sa.String(300))
    teor = sa.Column(sa.String(300))
    pr = sa.Column(sa.String(300))
    cr = sa.Column(sa.String(300))
    ects = sa.Column(sa.String(300))
    term = sa.Column(sa.String(300))

    user_id = sa.Column(UUID(as_uuid=True), ForeignKey("tbl_user.id"))
    user = relationship("User", back_populates="courses")

    curriculums = relationship("Curriculum", secondary=curriculum_course, back_populates="courses")
