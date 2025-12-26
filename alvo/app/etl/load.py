from dataclasses import dataclass

import pandas as pd
from sqlalchemy import insert, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.models.signal import Signal
from app.infra.models.target import TargetData


@dataclass
class Loader:
    db: AsyncSession

    async def _get_or_create_signals(self, signal_names: list[str]) -> dict[str, int]:
        """
        Garante que todos sinais existam no banco e retorna um mapa {nome: id}.
        """
        # 1. Buscar sinais existentes
        result = await self.db.execute(select(Signal))
        existing_signals = {s.name: s.id for s in result.scalars().all()}

        # 2. Identificar novos sinais
        new_signals = set(signal_names) - set(existing_signals.keys())

        if new_signals:
            # Inserir novos
            stmt = (
                insert(Signal)
                .values([{'name': name} for name in new_signals])
                .returning(Signal.id, Signal.name)
            )
            result = await self.db.execute(stmt)
            for row in result:
                existing_signals[row.name] = row.id

            # Commit das definições de sinais
            await self.db.commit()

        return existing_signals

    async def save_data(self, df: pd.DataFrame):
        """
        Recebe DataFrame processado (timestamp, value, signal_name) e salva no banco.
        """
        if df.empty:
            print('Nenhum dado para salvar.')
            return

        # 1. Resolver IDs dos Sinais
        unique_signals = df['signal_name'].unique().tolist()
        signal_map = await self._get_or_create_signals(unique_signals)

        # 2. Mapear nomes para IDs no DataFrame
        # Usa .map para criar a coluna signal_id
        df['signal_id'] = df['signal_name'].map(signal_map)

        # 3. Preparar lista de dicionários para inserção
        records = df[['timestamp', 'signal_id', 'value']].to_dict(orient='records')

        # 4. Upsert (Inserir ou Atualizar se já existir timestamp+signal_id)
        # Upsert do Postgres para evitar erro de duplicidade se rodar o ETL 2x
        stmt = pg_insert(TargetData).values(records)

        # Validar com PK ou Unique Constraint
        update_stmt = stmt.on_conflict_do_update(
            index_elements=['timestamp', 'signal_id'],
            set_={'value': stmt.excluded.value},
        )

        await self.db.execute(update_stmt)
        await self.db.commit()
        print(f'Sucesso: {len(records)} registros salvos/atualizados.')
