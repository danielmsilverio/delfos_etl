from datetime import datetime

from sqlalchemy.orm import (
    Mapped,
    mapped_as_dataclass,
    mapped_column,
    registry,
)

table_registry = registry()


@mapped_as_dataclass(table_registry)
class SensorData:
    __tablename__ = 'data'

    id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(nullable=False, index=True)
    wind_speed: Mapped[float] = mapped_column(nullable=True)
    power: Mapped[float] = mapped_column(nullable=True)
    ambient_temperature: Mapped[float] = mapped_column(nullable=True)
