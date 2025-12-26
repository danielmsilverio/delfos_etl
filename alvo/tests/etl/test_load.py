import pandas as pd
import pytest
from sqlalchemy import select

from app.etl.load import Loader
from app.infra.models.signal import Signal
from app.infra.models.target import TargetData


@pytest.mark.asyncio
async def test_save_data_empty(session):
    loader = Loader(db=session)
    df = pd.DataFrame()

    # Não deve gerar erro ao salvar um DataFrame vazio
    await loader.save_data(df)


@pytest.mark.asyncio
async def test_save_data_new_signals(session):
    loader = Loader(db=session)

    data = {
        'timestamp': [
            pd.Timestamp('2023-10-27 10:00:00'),
            pd.Timestamp('2023-10-27 10:00:00'),
        ],
        'signal_name': ['wind_speed_mean', 'power_max'],
        'value': [10.5, 100.0],
    }
    df = pd.DataFrame(data)

    await loader.save_data(df)

    # Verificar sinais criados
    result = await session.execute(select(Signal))
    signals = result.scalars().all()

    length_expected = 2
    assert len(signals) == length_expected

    signal_names = {s.name for s in signals}
    assert 'wind_speed_mean' in signal_names
    assert 'power_max' in signal_names

    # Verificar dados na tabela alvo
    result = await session.execute(select(TargetData))
    target_data = result.scalars().all()

    length_expected = 2
    assert len(target_data) == length_expected

    # Verificar valores
    for row in target_data:
        # Precisamos encontrar o nome do sinal para esta linha para verificar o valor
        signal = await session.get(Signal, row.signal_id)
        # obs: não gosto de usar ifs em testes, mas para este caso simples está ok
        if signal.name == 'wind_speed_mean':
            value_expected = 10.5
            assert row.value == value_expected
        elif signal.name == 'power_max':
            value_expected = 100.0
            assert row.value == value_expected


@pytest.mark.asyncio
async def test_save_data_upsert(session):
    loader = Loader(db=session)

    # Adicionar valor inicial
    data1 = {
        'timestamp': [pd.Timestamp('2023-10-27 10:00:00')],
        'signal_name': ['wind_speed_mean'],
        'value': [10.0],
    }
    df1 = pd.DataFrame(data1)
    await loader.save_data(df1)

    # Verificar valor inserido
    result = await session.execute(select(TargetData))
    rows = result.scalars().all()
    assert len(rows) == 1

    expected_value = 10.0
    assert rows[0].value == expected_value

    # Atualizar valor existente
    data2 = {
        'timestamp': [pd.Timestamp('2023-10-27 10:00:00')],
        'signal_name': ['wind_speed_mean'],
        'value': [20.0],
    }
    df2 = pd.DataFrame(data2)
    await loader.save_data(df2)

    # Verificar valor atualizado
    # Precisamos limpar o mapa de identidade da sessão ou consultar novamente para
    #   obter dados atualizados
    # Como o loader faz commit, o banco de dados é atualizado.
    # Mas a sessão pode ainda ter o objeto antigo no mapa de identidade se reutilizarmos
    #   o mesmo objeto de sessão sem expirar.
    # O fixture define expire_on_commit=False.
    # Então devemos expirar ou atualizar.
    session.expire_all()

    result = await session.execute(select(TargetData))
    rows = result.scalars().all()
    value_expected = 20.0
    assert len(rows) == 1
    assert rows[0].value == value_expected
