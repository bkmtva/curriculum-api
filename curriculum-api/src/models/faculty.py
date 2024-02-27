import sqlalchemy as sa
from sqlalchemy.orm import relationship
from src.models.base import Base, UUIDMixin


class Faculty(UUIDMixin, Base):
    __tablename__ = "tbl_faculty"

    title = sa.Column(sa.String(300))
    logo = sa.Column(sa.String(36))

    programs = relationship("Program", back_populates="faculty")
