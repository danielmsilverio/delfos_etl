#!/bin/sh
set -e

# 1. Aplica as migrações do banco de dados (Auto-migration)
echo "🔄 Rodando migrações do Alembic..."
uv run alembic upgrade head
echo "✅ Migrações aplicadas com sucesso!"

# 2. Executa o comando passado pelo Docker (CMD)
exec "$@"