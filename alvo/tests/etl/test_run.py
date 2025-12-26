from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import select

from app.etl.run import run_pipeline
from app.infra.models.signal import Signal
from app.infra.models.target import TargetData


@pytest.mark.asyncio
async def test_run_pipeline_integration(session):
    # 1. Preparar Dados Mockados
    target_date = datetime(2024, 1, 1)

    # Exemplo de dados brutos retornados pelo Extractor.get_raw_data (lista de dicts)
    # Baseado na lógica do transform.py, espera chaves:
    # 'timestamp', 'wind_speed', 'power', 'ambient_temperature'. E agrega a cada 10min.
    raw_data = [
        {
            'timestamp': '2024-01-01T00:00:00',
            'wind_speed': 10.0,
            'power': 100.0,
            'ambient_temperature': 25.0,
        },
        {
            'timestamp': '2024-01-01T00:05:00',  # Deve ser agregado com 00:00:00
            'wind_speed': 12.0,
            'power': 110.0,
            'ambient_temperature': 26.0,
        },
        {
            'timestamp': '2024-01-01T00:10:00',  # Próximo intervalo
            'wind_speed': 15.0,
            'power': 150.0,
            'ambient_temperature': 24.0,
        },
    ]

    # 2. Mockar Extractor e AsyncSessionLocal

    # Criar um mock para o context manager que AsyncSessionLocal retorna
    mock_session_cm = MagicMock()
    mock_session_cm.__aenter__ = AsyncMock(return_value=session)
    mock_session_cm.__aexit__ = AsyncMock(return_value=None)

    with (
        patch('app.etl.run.Extractor') as MockExtractor,
        patch('app.etl.run.AsyncSessionLocal', return_value=mock_session_cm),
    ):
        # Configurar a instância do mock extractor
        mock_extractor_instance = MockExtractor.return_value
        mock_extractor_instance.get_raw_data = AsyncMock(return_value=raw_data)

        # 3. Executar o pipeline
        await run_pipeline(target_date)

    # 4. Verificar Estado do Banco de Dados

    # Verificar Sinais
    # Esperamos sinais para wind_speed, power, ambient_temperature
    # E para cada: mean, min, max, std. Total 3 métricas * 4 stats = 12 sinais.
    result_signals = await session.execute(select(Signal))
    signals = result_signals.scalars().all()
    signal_names = {s.name for s in signals}

    expected_signals = {
        'wind_speed_mean',
        'wind_speed_min',
        'wind_speed_max',
        'wind_speed_std',
        'power_mean',
        'power_min',
        'power_max',
        'power_std',
        'ambient_temperature_mean',
        'ambient_temperature_min',
        'ambient_temperature_max',
        'ambient_temperature_std',
    }

    # Verificar se todos os sinais esperados estão presentes
    assert expected_signals.issubset(signal_names)

    # Verificar Dados
    # Temos 2 intervalos: 00:00 e 00:10.
    # Para 00:00 (agregado de 00:00 e 00:05):
    # wind_speed mean = (10+12)/2 = 11.0

    # Encontrar o ID do sinal para wind_speed_mean
    wind_speed_mean_signal = next(s for s in signals if s.name == 'wind_speed_mean')

    stmt = select(TargetData).where(
        TargetData.timestamp == datetime(2024, 1, 1, 0, 0, 0),
        TargetData.signal_id == wind_speed_mean_signal.id,
    )
    result_data = await session.execute(stmt)
    data_entry = result_data.scalar_one_or_none()

    assert data_entry is not None
    value_expected = 11.0
    assert data_entry.value == value_expected

    # Verificar contagem total de pontos de dados
    result_all_data = await session.execute(select(TargetData))
    all_data = result_all_data.scalars().all()
    assert len(all_data) > 0
