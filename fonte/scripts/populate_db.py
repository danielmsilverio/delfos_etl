import asyncio
import os
import sys
from datetime import datetime

# Adiciona o diretório pai ao path para conseguir importar 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import AsyncSessionLocal
from app.services.seeder import DataSeeder


async def main():
    print('Iniciando população do banco de dados...')

    # Define a data inicial fixa ou dinâmica
    start_date = datetime(2025, 3, 1, 0, 0, 0)
    days = 10

    async with AsyncSessionLocal() as session:
        seeder = DataSeeder(session)
        result = await seeder.generate_data(start_date, days)

    print(f'Sucesso! {result["total_records"]} registros inseridos.')
    print(f'Período: {result["start"]} até {result["end"]}')


if __name__ == '__main__':
    asyncio.run(main())
