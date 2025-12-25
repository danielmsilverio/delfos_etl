from datetime import datetime

import pytest
from sqlalchemy import func, select

from app.models.sensor import SensorData
from app.services.seeder import DataSeeder


@pytest.mark.asyncio
async def test_generate_data_integration(session):
    # 1. Setup
    seeder = DataSeeder(session)
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    days = 1  # Testar com 1 dia para ser rápido (1440 registros)

    # 2. Execução
    result = await seeder.generate_data(start_date, days)

    # 3. Verificações do Retorno
    expected_count = days * 24 * 60
    assert result['total_records'] == expected_count
    assert result['start'] == start_date

    # 4. Verificações no Banco (Side Effects)
    # Conta quantos registros foram inseridos
    stmt = select(func.count()).select_from(SensorData)
    db_result = await session.execute(stmt)
    count = db_result.scalar()

    expected_count = days * 24 * 60
    assert count == expected_count

    # Verifica se os dados parecem corretos (amostra)
    stmt_sample = select(SensorData).limit(1)
    sample = (await session.execute(stmt_sample)).scalar_one()

    assert sample.wind_speed is not None
    assert sample.power is not None
    # Verifica intervalo de valores (sanity check)
    wind_speed_started = 0
    wind_speed_ended = 25
    assert wind_speed_started <= sample.wind_speed <= wind_speed_ended
