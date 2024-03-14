# import sqlalchemy as sa
# from sqlalchemy import ForeignKey
# from sqlalchemy.dialects.postgresql import UUID
# from src.models.base import Base
#
#
# curriculum_course = sa.Table(
#     'curriculum_course', Base.metadata,
#     sa.Column('curriculum_id', UUID, ForeignKey("tbl_curriculum.id", ondelete='CASCADE')),
#     sa.Column('course_id', UUID, ForeignKey("tbl_course.id", ondelete='CASCADE')),
#     sa.Column('semester', sa.Integer, nullable=False),
#     sa.Column('order_in_semester', sa.Integer, nullable=False)
# )
