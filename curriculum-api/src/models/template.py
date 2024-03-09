import sqlalchemy as sa
from sqlalchemy.orm import relationship
from src.models.base import Base, UUIDMixin
# from src.models.program import Program


class Template(UUIDMixin, Base):
    __tablename__ = "tbl_template"

    title = sa.Column(sa.String(300))
    semester_count = sa.Column(sa.Integer, default=8)

    programs = relationship("Program", back_populates="template")
