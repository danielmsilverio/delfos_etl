import pandas as pd

from app.etl.transform import Transformer


def test_process_data_empty():
    result = Transformer.process_data([])

    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_process_data_success():
    raw_data = [
        {
            'timestamp': '2023-10-27T10:00:00',
            'wind_speed': 10.0,
            'power': 100.0,
            'ambient_temperature': 25.0,
        },
        {
            'timestamp': '2023-10-27T10:05:00',
            'wind_speed': 20.0,
            'power': 200.0,
            'ambient_temperature': 27.0,
        },
        # Adicionando 10 minutos depois para testar múltiplas janelas
        {
            'timestamp': '2023-10-27T10:10:00',
            'wind_speed': 15.0,
            'power': 150.0,
            'ambient_temperature': 26.0,
        },
    ]

    result = Transformer.process_data(raw_data)

    assert not result.empty
    assert 'timestamp' in result.columns
    assert 'signal_name' in result.columns
    assert 'value' in result.columns

    # Validar agregação para a primeira janela (10:00 - 10:10)
    # wind_speed mean: (10+20)/2 = 15
    wind_speed_mean = result[
        (result['timestamp'] == pd.Timestamp('2023-10-27 10:00:00'))
        & (result['signal_name'] == 'wind_speed_mean')
    ]['value'].iloc[0]

    expected_value = 15.0
    assert wind_speed_mean == expected_value

    # Validar agregação para a segunda janela (10:10 - 10:20)
    # wind_speed mean: 15
    wind_speed_mean_2 = result[
        (result['timestamp'] == pd.Timestamp('2023-10-27 10:10:00'))
        & (result['signal_name'] == 'wind_speed_mean')
    ]['value'].iloc[0]

    expected_value = 15.0
    assert wind_speed_mean_2 == expected_value


def test_process_data_missing_metrics():
    raw_data = [
        {
            'timestamp': '2023-10-27T10:00:00',
            'wind_speed': 10.0,
        }
    ]

    result = Transformer.process_data(raw_data)

    assert not result.empty
    unique_signals = result['signal_name'].unique()

    # Apresentar apenas sinais relacionados ao wind_speed
    assert any('wind_speed' in s for s in unique_signals)
    assert not any('power' in s for s in unique_signals)
    assert not any('ambient_temperature' in s for s in unique_signals)
