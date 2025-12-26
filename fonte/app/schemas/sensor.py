from datetime import UTC, datetime
from typing import Literal

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field

# Opções válidas para o filtro de colunas
MetricType = Literal['wind_speed', 'power', 'ambient_temperature']


class SensorDataBase(BaseModel):
    timestamp: datetime
    wind_speed: float | None = None
    power: float | None = None
    ambient_temperature: float | None = None

    model_config = ConfigDict(from_attributes=True)


class SensorDataCreate(SensorDataBase):
    pass


class SensorDataResponse(SensorDataBase):
    pass


class SensorDataFilter(BaseModel):
    start_date: datetime
    end_date: datetime
    metrics: list[MetricType] | None = Query(
        default=None, description='Selecione as variáveis desejadas'
    )

    model_config = ConfigDict(from_attributes=True)


class InertialSensorDataStructure(BaseModel):
    start_date: datetime = Field(
        ...,
        description='Data de início para geração dos dados',
        default_factory=datetime.now(UTC),
    )
    days: int = 10
