from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.models.sensor import SensorData


@dataclass
class SensorRepository:
    db: AsyncSession

    async def insert_sensor_data(
        db: AsyncSession,
        timestamp: datetime,
        wind_speed: float | None = None,
        power: float | None = None,
        ambient_temperature: float | None = None,
    ) -> SensorData:
        new_data = SensorData(
            timestamp=timestamp,
            wind_speed=wind_speed,
            power=power,
            ambient_temperature=ambient_temperature,
        )
        db.add(new_data)
        await db.commit()
        await db.refresh(new_data)
        return new_data

    async def get_sensor_data_by_id(
        db: AsyncSession, data_id: int
    ) -> SensorData | None:  # noqa E501
        result = await db.get(SensorData, data_id)
        return result

    async def get_data_by_range(
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime,
        metrics: list[str] | None = None,
    ) -> list[SensorData] | list[dict]:

        # Se métricas foram especificadas, selecionamos apenas essas colunas + timestamp
        if metrics:
            cols_to_select = [SensorData.timestamp]
            for metric in metrics:
                # Garante que a coluna existe no model para evitar injeção ou erro
                if hasattr(SensorData, metric):
                    cols_to_select.append(getattr(SensorData, metric))

            stmt = select(*cols_to_select)
        else:
            # Se não passar métricas, traz o objeto inteiro
            stmt = select(SensorData)

        # Aplica filtros de data
        stmt = stmt.where(
            SensorData.timestamp >= start_date, SensorData.timestamp <= end_date
        ).order_by(SensorData.timestamp.asc())

        result = await db.execute(stmt)

        if metrics:
            # SQLAlchemy retorna Rows (tuplas) quando selecionamos colunas específicas.
            # Convertemos para dict para o Pydantic entender.
            rows = result.all()
            return [
                {
                    'timestamp': row.timestamp,
                    **{m: getattr(row, m, None) for m in metrics},
                }
                for row in rows
            ]

        # Se selecionou o objeto inteiro (ORM), retorna scalars
        return result.scalars().all()

    async def insert_bulk_sensor_data(
        db: AsyncSession,
        data_list: list[dict],
    ) -> None:
        """
        Insere múltiplos registros na tabela 'data' em uma única operação.
        Cada dicionário em data_list deve conter as chaves correspondentes
        às colunas da tabela.
        """
        await db.execute(insert(SensorData).values(data_list))
