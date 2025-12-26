from datetime import datetime
from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from app.etl.extract import Extractor


@pytest.mark.asyncio
async def test_get_raw_data_success_date_only():
    # Preparar mock
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = Mock()
    mock_response.json.return_value = [{'id': 1, 'value': 10}]
    mock_response.raise_for_status.return_value = None
    mock_client.get.return_value = mock_response

    extractor = Extractor(client=mock_client)
    date = datetime(2023, 10, 27)

    result = await extractor.get_raw_data(date=date)

    assert result == [{'id': 1, 'value': 10}]
    mock_client.get.assert_called_once()

    # Verificar resultados
    args, kwargs = mock_client.get.call_args
    assert kwargs['params']['start_date'] == '2023-10-27T00:00:00'
    assert kwargs['params']['end_date'] == '2023-10-27T23:59:59'
    assert 'metrics' not in kwargs['params']

    # Verificar limpeza
    mock_client.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_get_raw_data_success_with_metrics():
    # Preparar mock
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = Mock()
    mock_response.json.return_value = [{'id': 1, 'value': 10}]
    mock_response.raise_for_status.return_value = None
    mock_client.get.return_value = mock_response

    extractor = Extractor(client=mock_client)
    date = datetime(2023, 10, 27)
    metrics = ['temperature', 'humidity']

    result = await extractor.get_raw_data(date=date, metrics=metrics)

    # Verificar resultado
    assert result == [{'id': 1, 'value': 10}]
    mock_client.get.assert_called_once()

    args, kwargs = mock_client.get.call_args
    assert kwargs['params']['metrics'] == metrics

    # Verificar limpeza
    mock_client.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_get_raw_data_http_error():
    # Preparar mock
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.side_effect = httpx.HTTPError('Error connecting')

    extractor = Extractor(client=mock_client)
    date = datetime(2023, 10, 27)

    with pytest.raises(httpx.HTTPError):
        await extractor.get_raw_data(date=date)

    mock_client.get.assert_called_once()

    # Verificar limpeza
    mock_client.aclose.assert_called_once()
