from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import (
    Mapped,
    mapped_as_dataclass,
    mapped_column,
    relationship,
)

from . import table_registry

if TYPE_CHECKING:
    from .signal import Signal


@mapped_as_dataclass(table_registry)
class TargetData:
    __tablename__ = 'data'

    timestamp: Mapped[DateTime] = mapped_column(
        DateTime, primary_key=True, nullable=False
    )
    signal_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('signal.id'), primary_key=True, nullable=False
    )
    value: Mapped[float] = mapped_column(Float, nullable=True)
    signal: Mapped['Signal'] = relationship('Signal', back_populates='data_points')

    __table_args__ = (
        UniqueConstraint('timestamp', 'signal_id', name='uix_timestamp_signal'),
    )
