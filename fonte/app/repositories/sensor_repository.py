from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sensor import SensorData


class SensorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_data_by_range(
        self,
        start_date: datetime,
        end_date: datetime,
        metrics: Optional[List[str]] = None,
    ) -> List[Any]:

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

        result = await self.db.execute(stmt)

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
