from dataclasses import dataclass
from datetime import datetime, timedelta

import httpx

from app.config.config import settings


@dataclass
class Extractor:
    client: httpx.AsyncClient = httpx.AsyncClient(
        base_url=settings.SOURCE_API_URL, timeout=30.0
    )

    async def get_raw_data(
        self, date: datetime, metrics: list[str] | None = None
    ) -> list[dict[str, any]]:  # noqa: E501
        """
        Busca dados de um dia inteiro na API Fonte.
        """
        # Define o intervalo do dia (00:00 até 23:59:59)
        start_time = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1) - timedelta(seconds=1)

        params = {
            'start_date': start_time.isoformat(),
            'end_date': end_time.isoformat(),
        }

        if metrics:
            params['metrics'] = metrics

        try:
            response = await self.client.get('/sensors', params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f'Erro ao extrair dados: {e}')
            raise
        finally:
            await self.client.aclose()
