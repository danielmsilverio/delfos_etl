from datetime import datetime
from http import HTTPStatus


def test_seed_endpoint_creates_data(client):
    payload = {
        'start_date': datetime(2024, 1, 1, 0, 0, 0).isoformat(),
        'days': 1,
    }

    resp = client.post('/api/seed', json=payload)
    assert resp.status_code == HTTPStatus.CREATED

    body = resp.json()
    assert body['message'] == 'Dados inseridos com sucesso'

    details = body['details']
    assert details['total_records'] == 24 * 60  # 1 dia -> 1440 registros
    assert 'start' in details
    assert 'end' in details


def test_seed_endpoint_invalid_payload(client):
    payload = {
        'start_date': 'invalid-date-format',
        'days': -5,
    }

    resp = client.post('/api/seed', json=payload)
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_seed_endpoint_server_error(client, monkeypatch):
    def mock_generate_data(self, start_date, days):
        raise Exception('Simulated database error')

    monkeypatch.setattr(
        'app.services.seeder.DataSeeder.generate_data', mock_generate_data
    )

    payload = {
        'start_date': datetime(2024, 1, 1, 0, 0, 0).isoformat(),
        'days': 1,
    }

    resp = client.post('/api/seed', json=payload)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    body = resp.json()
    assert body['detail'] == 'Simulated database error'
