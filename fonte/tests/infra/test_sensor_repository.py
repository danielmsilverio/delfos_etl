from datetime import datetime, timedelta

import pytest

from app.infra.models.sensor import SensorData
from app.infra.repositories.sensor_repository import SensorRepository


@pytest.mark.asyncio
async def test_insert_sensor_data(session):
    # 1. Setup: Dados a serem inseridos
    timestamp = datetime(2025, 1, 1, 12, 0, 0)
    wind_speed = 10.5
    power = 100.0
    ambient_temperature = 25.0

    # 2. Execução: Inserir dados
    new_data = await SensorRepository.insert_sensor_data(
        session,
        timestamp=timestamp,
        wind_speed=wind_speed,
        power=power,
        ambient_temperature=ambient_temperature,
    )

    assert new_data is not None
    assert new_data.timestamp == timestamp
    assert new_data.wind_speed == wind_speed
    assert new_data.power == power
    assert new_data.ambient_temperature == ambient_temperature


@pytest.mark.asyncio
async def test_get_sensor_data_by_id(session):
    # 1. Setup: Inserir dados para teste
    timestamp = datetime(2025, 1, 1, 12, 0, 0)
    wind_speed = 10.5
    power = 100.0
    ambient_temperature = 25.0

    new_data = await SensorRepository.insert_sensor_data(
        session,
        timestamp=timestamp,
        wind_speed=wind_speed,
        power=power,
        ambient_temperature=ambient_temperature,
    )

    # 2. Execução: Buscar pelos dados inseridos
    fetched_data = await SensorRepository.get_sensor_data_by_id(session, new_data.id)

    # 3. Verificação
    assert fetched_data is not None
    assert fetched_data.id == new_data.id
    assert fetched_data.timestamp == timestamp
    assert fetched_data.wind_speed == wind_speed
    assert fetched_data.power == power
    assert fetched_data.ambient_temperature == ambient_temperature


@pytest.mark.asyncio
async def test_get_sensor_data_by_id_not_found(session):
    # Execução: Buscar um ID que não existe
    fetched_data = await SensorRepository.get_sensor_data_by_id(session, 9999)

    # Verificação
    assert fetched_data is None


@pytest.mark.asyncio
async def test_get_data_by_range_success(session):
    now = datetime(2025, 1, 1, 12, 0, 0)
    wind_speed = 10.5
    power = 100.0
    ambient_temperature = 25.0

    data1 = await SensorRepository.insert_sensor_data(
        session,
        timestamp=now,
        wind_speed=wind_speed,
        power=power,
        ambient_temperature=ambient_temperature,
    )

    timestamp = datetime(2025, 1, 1, 12, 1, 0)
    wind_speed = 12.0
    power = 150.0
    ambient_temperature = 26.0

    await SensorRepository.insert_sensor_data(
        session,
        timestamp=timestamp,
        wind_speed=wind_speed,
        power=power,
        ambient_temperature=ambient_temperature,
    )

    # 2. Execução: Buscar intervalo
    results: list[SensorData] = await SensorRepository.get_data_by_range(
        session, start_date=now, end_date=now + timedelta(seconds=30)
    )

    # 3. Verificação
    assert len(results) == 1
    assert results[0].wind_speed == data1.wind_speed
    assert results[0].power == data1.power
    assert results[0].ambient_temperature == data1.ambient_temperature


@pytest.mark.asyncio
async def test_get_data_with_dynamic_columns(session):
    # Setup
    now = datetime(2025, 1, 1, 12, 0, 0)
    wind_speed = 10.5
    power = 100.0
    ambient_temperature = 25.0

    data1 = await SensorRepository.insert_sensor_data(
        session,
        timestamp=now,
        wind_speed=wind_speed,
        power=power,
        ambient_temperature=ambient_temperature,
    )

    # Selecionar apenas wind_speed
    results: list[dict] = await SensorRepository.get_data_by_range(
        session, start_date=now, end_date=now, metrics=['wind_speed']
    )

    assert len(results) == 1
    # O repositório deve retornar um dict quando passamos métricas
    assert 'wind_speed' in results[0]
    assert 'power' not in results[0]
    assert results[0]['wind_speed'] == data1.wind_speed
    assert results[0]['timestamp'] == data1.timestamp
