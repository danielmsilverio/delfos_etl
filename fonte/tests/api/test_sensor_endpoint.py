from datetime import datetime, timedelta
from http import HTTPStatus

import pytest

from app.infra.repositories.sensor_repository import SensorRepository


@pytest.mark.asyncio
async def test_create_sensor_data_success(client):
    payload = {
        'timestamp': datetime(2025, 1, 1, 12, 0, 0).isoformat(),
        'wind_speed': 10.5,
        'power': 100.0,
        'ambient_temperature': 25.0,
    }

    resp = client.post('/api/v1/sensors', json=payload)
    assert resp.status_code == HTTPStatus.CREATED

    body = resp.json()
    assert body['timestamp'] == payload['timestamp']
    assert body['wind_speed'] == payload['wind_speed']
    assert body['power'] == payload['power']
    assert body['ambient_temperature'] == payload['ambient_temperature']


@pytest.mark.asyncio
async def test_create_sensor_data_invalid_payload(client):
    payload = {
        'timestamp': 'invalid-date-format',
        'wind_speed': -5,  # Valor inválido
        'power': 'not-a-number',  # Tipo inválido
        # ambient_temperature está faltando
    }

    resp = client.post('/api/v1/sensors', json=payload)
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_sensor_data_returns_full_objects(client, session):
    now = datetime(2025, 1, 1, 12, 0, 0)
    await SensorRepository.insert_sensor_data(
        db=session,
        timestamp=now,
        wind_speed=10.5,
        power=100.0,
        ambient_temperature=25.0,
    )

    params = {
        'start_date': now.isoformat(),
        'end_date': (now + timedelta(minutes=1)).isoformat(),
    }

    resp = client.get('/api/v1/sensors', params=params)
    assert resp.status_code == HTTPStatus.OK

    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == 1
    item = body[0]
    response_expected = {
        'timestamp': now.isoformat(),
        'wind_speed': 10.5,
        'power': 100.0,
        'ambient_temperature': 25.0,
    }
    assert item == response_expected


@pytest.mark.asyncio
async def test_get_sensor_data_returns_400_when_start_after_end(client):
    params = {
        'start_date': datetime(2025, 1, 2, 0, 0, 0).isoformat(),
        'end_date': datetime(2025, 1, 1, 0, 0, 0).isoformat(),
    }

    resp = client.get('/api/v1/sensors', params=params)

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json()['detail'] == 'start_date deve ser menor que end_date'


@pytest.mark.asyncio
async def test_get_sensor_data_with_metrics_returns_selected_fields(client, session):
    now = datetime(2025, 1, 1, 12, 0, 0)
    await SensorRepository.insert_sensor_data(
        db=session,
        timestamp=now,
        wind_speed=10.5,
        power=100.0,
        ambient_temperature=25.0,
    )

    params = {
        'start_date': now.isoformat(),
        'end_date': now.isoformat(),
        'metrics': ['wind_speed'],
    }

    resp = client.get('/api/v1/sensors', params=params)
    assert resp.status_code == HTTPStatus.OK

    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == 1
    item = body[0]
    # As response_model inclui todos os campos, os não selecionados devem ser None
    wind_speed_expected = 10.5
    assert item['wind_speed'] == wind_speed_expected
    assert item['power'] is None
    assert item['ambient_temperature'] is None


@pytest.mark.asyncio
async def test_get_sensor_data_with_invalid_metric_returns_422(client):
    now = datetime(2025, 1, 1, 12, 0, 0)
    params = {
        'start_date': now.isoformat(),
        'end_date': now.isoformat(),
        'metrics': ['invalid_metric'],
    }

    resp = client.get('/api/v1/sensors', params=params)
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_populate_database(client):
    payload = {
        'start_date': datetime(2024, 1, 1, 0, 0, 0).isoformat(),
        'days': 1,
    }

    resp = client.post('/api/v1/sensors/populate_database', json=payload)
    assert resp.status_code == HTTPStatus.CREATED

    body = resp.json()
    expected_response = {
        'message': 'Dados inseridos com sucesso',
        'details': {
            'total_records': 1440,
            'start': '2024-01-01T00:00:00',
            'end': '2024-01-02T00:00:00',
        },
    }
    assert body == expected_response


@pytest.mark.asyncio
async def test_populate_database_invalid_payload(client):
    payload = {
        'start_date': 'invalid-date-format',
        'days': -5,
    }

    resp = client.post('/api/v1/sensors/populate_database', json=payload)
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_populate_database_server_error(client, monkeypatch):
    def mock_generate_data(self, start_date, days):
        raise Exception('Simulated database error')

    monkeypatch.setattr(
        'app.services.sensor_data_generator.SensorDataGenerator.generate_data',
        mock_generate_data,
    )

    payload = {
        'start_date': datetime(2024, 1, 1, 0, 0, 0).isoformat(),
        'days': 1,
    }

    resp = client.post('/api/v1/sensors/populate_database', json=payload)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    body = resp.json()
    assert body['detail'] == 'Simulated database error'
