import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from src.models.base import Base, UUIDMixin, CreatedUpdatedMixin
from src.models.curriculum import Curriculum
from src.models.template import Template


class Program(UUIDMixin, CreatedUpdatedMixin, Base):
    __tablename__ = "tbl_program"

    title = sa.Column(sa.String(300))
    code = sa.Column(sa.String(36))
    cipher = sa.Column(sa.String(36))
    ects = sa.Column(sa.String(36))

    degree_id = sa.Column(UUID(as_uuid=True), ForeignKey("tbl_degree.id"))
    degree = relationship("Degree", back_populates="programs")

    template_id = sa.Column(UUID(as_uuid=True), ForeignKey("tbl_template.id"))
    template = relationship("Template", back_populates="programs")

    curriculums = relationship("Curriculum", back_populates="program")
