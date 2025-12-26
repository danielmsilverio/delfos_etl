from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import (
    Mapped,
    mapped_as_dataclass,
    mapped_column,
    relationship,
)

from . import table_registry

if TYPE_CHECKING:
    from .target import TargetData


@mapped_as_dataclass(table_registry)
class Signal:
    __tablename__ = 'signal'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    data_points: Mapped[list['TargetData']] = relationship(
        'TargetData', back_populates='signal'
    )
