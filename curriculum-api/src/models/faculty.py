import sqlalchemy as sa
from sqlalchemy.orm import relationship
from src.models.base import Base, UUIDMixin


class Program(UUIDMixin, Base):
    __tablename__ = "tbl_program"

    title = sa.Column(sa.String(300))
    cipher = sa.Column(sa.String(36))
    level = sa.Column(sa.String(36))
    users = relationship("User", back_populates="faculty")

class Faculty(UUIDMixin, Base):
    __tablename__ = "tbl_faculty"

    title = sa.Column(sa.String(300))
    cipher = sa.Column(sa.String(36))
    level = sa.Column(sa.String(36))
    users = relationship("User", back_populates="faculty")
