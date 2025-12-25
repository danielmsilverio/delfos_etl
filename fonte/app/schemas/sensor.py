from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# Opções válidas para o filtro de colunas
MetricType = Literal['wind_speed', 'power', 'ambient_temperature']


class SensorDataResponse(BaseModel):
    timestamp: datetime
    wind_speed: float | None = None
    power: float | None = None
    ambient_temperature: float | None = None

    model_config = ConfigDict(from_attributes=True)


class SensorDataFilter(BaseModel):
    start_date: datetime
    end_date: datetime
    metrics: list[MetricType] | None = Field(
        description='Selecione as variáveis desejadas'
    )
    model_config = ConfigDict(from_attributes=True)
