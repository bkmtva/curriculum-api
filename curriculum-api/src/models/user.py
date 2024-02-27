import sqlalchemy as sa
from sqlalchemy import ForeignKey
from src.models.base import Base, UUIDMixin
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


class User(UUIDMixin, Base):
    __tablename__ = "tbl_user"

    first_name = sa.Column(sa.String(255))
    last_name = sa.Column(sa.String(255))
    hashed_password = sa.Column(sa.String(255), nullable=False)
    email = sa.Column(sa.String(255), nullable=False, unique=True)
    profile_image = sa.Column(sa.String(255))
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False)
    last_login_at = sa.Column(sa.DateTime)
    is_active = sa.Column(sa.Boolean, default=True)
    is_superuser = sa.Column(sa.Boolean, default=False)
    program_id = sa.Column(UUID(as_uuid=True), ForeignKey('tbl_program.id'))
    program = relationship("Program", back_populates="users")

    def update_last_login(self):
        self.last_login_at = datetime.utcnow()
