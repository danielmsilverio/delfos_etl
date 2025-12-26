import random
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.repositories.sensor_repository import SensorRepository


@dataclass
class SensorDataGenerator:
    db: AsyncSession

    async def generate_data(self, start_date: datetime, days: int = 10):
        """
        Gera dados minuto a minuto e insere em lote (Bulk Insert).
        """
        total_minutes = days * 24 * 60
        data_batch = []

        current_time = start_date

        # Geração dos dados em memória
        for _ in range(total_minutes):
            record = {
                'timestamp': current_time,
                'wind_speed': round(random.uniform(0, 25), 2),
                'power': round(random.uniform(0, 5000), 2),  # Ex: kW
                'ambient_temperature': round(random.uniform(15, 35), 2),
            }
            data_batch.append(record)
            current_time += timedelta(minutes=1)

        # Inserção em lote no Banco
        # Quebramos em chunks de 10.000 para não estourar memória se for muitos dias
        chunk_size = 10000
        for i in range(0, len(data_batch), chunk_size):
            chunk = data_batch[i : i + chunk_size]
            await SensorRepository.insert_bulk_sensor_data(self.db, chunk)

        await self.db.commit()

        return {
            'total_records': len(data_batch),
            'start': start_date,
            'end': current_time,
        }
