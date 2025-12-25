from datetime import datetime, timedelta

import pytest

from app.models.sensor import SensorData
from app.repositories.sensor_repository import SensorRepository


@pytest.mark.asyncio
async def test_get_data_by_range_success(session):
    now = datetime(2025, 1, 1, 12, 0, 0)
    data1 = SensorData(
        timestamp=now, wind_speed=10.5, power=100.0, ambient_temperature=25.0
    )
    data2 = SensorData(
        timestamp=now + timedelta(minutes=1),
        wind_speed=12.0,
        power=150.0,
        ambient_temperature=26.0,
    )
    session.add_all([data1, data2])
    await session.commit()

    repo = SensorRepository(session)

    # 2. Execução: Buscar intervalo
    results = await repo.get_data_by_range(
        start_date=now, end_date=now + timedelta(seconds=30)
    )

    # 3. Verificação
    wind_speed_expected = 10.5
    assert len(results) == 1
    assert results[0].wind_speed == wind_speed_expected


@pytest.mark.asyncio
async def test_get_data_with_dynamic_columns(session):
    # Setup
    now = datetime(2025, 1, 1, 12, 0, 0)
    session.add(
        SensorData(
            timestamp=now, wind_speed=10.5, power=100.0, ambient_temperature=25.0
        )
    )
    await session.commit()

    repo = SensorRepository(session)

    # Selecionar apenas wind_speed
    results = await repo.get_data_by_range(
        start_date=now, end_date=now, metrics=['wind_speed']
    )

    assert len(results) == 1
    # O repositório deve retornar um dict quando passamos métricas
    wind_speed_expected = 10.5
    assert 'wind_speed' in results[0]
    assert 'power' not in results[0]
    assert results[0]['wind_speed'] == wind_speed_expected
