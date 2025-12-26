import argparse
import asyncio
import logging
import sys
from datetime import datetime

from app.etl.run import run_pipeline

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description='Executa o ETL da Delfos')
    parser.add_argument(
        '--date',
        type=str,
        help='Data para processamento no formato YYYY-MM-DD (Padrão: ontem)',
        default=None,
    )
    return parser.parse_args()


async def main():
    logger.info('🚀 Iniciando o pipeline ETL da Delfos')
    args = parse_args()

    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d')
        except ValueError:
            logger.error('❌ Erro: Formato de data inválido. Use YYYY-MM-DD.')
            sys.exit(1)
    else:
        # Se não passar data, assume "ontem" ou "hoje"
        target_date = datetime.now()

    await run_pipeline(target_date)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.error('\nOperação cancelada pelo usuário.')
