import sqlalchemy as sa
from sqlalchemy import ForeignKey
from src.models.base import Base, UUIDMixin, CreatedUpdatedMixin
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from src.models.faculty import Faculty


class User(UUIDMixin, CreatedUpdatedMixin, Base):
    __tablename__ = "tbl_user"

    first_name = sa.Column(sa.String(255))
    last_name = sa.Column(sa.String(255))
    password = sa.Column(sa.String(255))
    email = sa.Column(sa.String(255), unique=True)
    profile_image = sa.Column(sa.String(255))
    # created_at = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False)
    last_login_at = sa.Column(sa.DateTime)
    is_active = sa.Column(sa.Boolean, default=True)
    is_superuser = sa.Column(sa.Boolean, default=False)

    faculty_id = sa.Column(UUID(as_uuid=True), ForeignKey("tbl_faculty.id"))
    faculty = relationship("Faculty", back_populates="users")

    courses = relationship("Course", back_populates="user")
    curriculums = relationship("Curriculum", back_populates="user")
    histories = relationship("CurriculumEditHistory", back_populates="user")

    def update_last_login(self):
        self.last_login_at = datetime.utcnow()
