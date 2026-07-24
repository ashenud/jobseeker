from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared SQLAlchemy metadata foundation.

    Domain tables remain owned by Milestone 06.
    """
