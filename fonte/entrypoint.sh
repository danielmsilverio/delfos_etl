#!/bin/sh
set -e

# 1. Aplica as migrações do banco de dados (Auto-migration)
echo "🔄 Rodando migrações do Alembic..."
uv run alembic upgrade head
echo "✅ Migrações aplicadas com sucesso!"

# 2. Iniciar a Aplicação
echo "Iniciando servidor FastAPI..."
exec fastapi run app/main.py --port 8000 --host 0.0.0.0