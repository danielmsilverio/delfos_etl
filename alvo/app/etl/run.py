from datetime import datetime

from app.etl.extract import Extractor
from app.etl.load import Loader
from app.etl.transform import Transformer
from app.infra.database.database import AsyncSessionLocal


async def run_pipeline(target_date: datetime):
    print(f'🚀 Iniciando Pipeline ETL para {target_date.date()}...')

    # 1. Extract
    print('--- Extraindo dados da Fonte ---')
    extractor = Extractor()
    try:
        raw_data = await extractor.get_raw_data(target_date)
        print(f'📥 Dados extraídos: {len(raw_data)} registros.')
    except Exception as e:
        print(f'❌ Erro na extração: {e}')
        return

    # 2. Transform
    print('--- Transformando dados ---')
    transformer = Transformer()
    df_clean = transformer.process_data(raw_data)

    if df_clean.empty:
        print('⚠️ Nenhum dado para processar após transformação.')
        return

    print(f'📊 Dados transformados: {len(df_clean)} registros (agregados).')

    # 3. Load
    print('--- Carregando no Banco Alvo ---')
    async with AsyncSessionLocal() as db:
        loader = Loader(db)
        await loader.save_data(df_clean)

    print('✅ Pipeline finalizado com sucesso!')
