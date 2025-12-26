from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.database.database import get_session
from app.infra.repositories.sensor_repository import SensorRepository
from app.schemas.sensor import (
    InertialSensorDataStructure,
    SensorDataCreate,
    SensorDataFilter,
    SensorDataResponse,
)
from app.services.sensor_data_generator import SensorDataGenerator

router = APIRouter(prefix='/sensors', tags=['sensors'])

Session = Annotated[AsyncSession, Depends(get_session)]


@router.get('', response_model=list[SensorDataResponse])
async def get_sensor_data(
    filter: Annotated[SensorDataFilter, Query()],
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

    print('Fetching sensor data with filter:', filter)
    results = await SensorRepository.get_data_by_range(
        db, filter.start_date, filter.end_date, filter.metrics
    )
    return results


@router.post('', status_code=201, response_model=SensorDataResponse)
async def create_sensor_data(
    data: SensorDataCreate,
    db: Session,
):
    """
    Insere um novo registro na tabela 'data'.
    """
    new_data = await SensorRepository.insert_sensor_data(
        db,
        timestamp=data.timestamp,
        wind_speed=data.wind_speed,
        power=data.power,
        ambient_temperature=data.ambient_temperature,
    )
    return new_data


@router.post('/populate_database', status_code=201)
async def populate_database(
    payload: InertialSensorDataStructure,
    db: Session,
):
    """
    Endpoint para popular o banco de dados.
    """
    generator = SensorDataGenerator(db)
    try:
        result = await generator.generate_data(payload.start_date, payload.days)
        return {'message': 'Dados inseridos com sucesso', 'details': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
