from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.repositories.sensor_repository import SensorRepository
from app.schemas.sensor import SensorDataFilter, SensorDataResponse

router = APIRouter()

Session = Annotated[AsyncSession, Depends(get_session)]


@router.get('/data', response_model=list[SensorDataResponse])
async def get_sensor_data(
    filter: Annotated[SensorDataFilter, Depends()],
    db: Session,
):
    """
    Retorna dados da tabela 'data' filtrados por intervalo de tempo.
    Permite selecionar colunas específicas.
    """
    if filter.start_date > filter.end_date:
        raise HTTPException(
            status_code=400, detail='start_date deve ser menor que end_date'
        )

    repo = SensorRepository(db)
    results = await repo.get_data_by_range(
        filter.start_date, filter.end_date, filter.metrics
    )
    return results
