import sqlalchemy as sa
from sqlalchemy.orm import relationship
from src.models.base import Base, UUIDMixin, CreatedUpdatedMixin
from src.models.degree import Degree


class Faculty(UUIDMixin,  CreatedUpdatedMixin, Base):
    __tablename__ = "tbl_faculty"

    title = sa.Column(sa.String(300))
    logo = sa.Column(sa.String(36))

    degrees = relationship("Degree", back_populates="faculty")
    users = relationship("User", back_populates="faculty")

