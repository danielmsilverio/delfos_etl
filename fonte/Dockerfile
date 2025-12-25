FROM python:3.12-slim

# Instalar o uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Configurações para o Python e UV
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Garante que o uv compile para bytecode para performance
ENV UV_COMPILE_BYTECODE=1

WORKDIR /app

# 1. Copiar arquivos de dependência
COPY pyproject.toml uv.lock ./

# 2. Instalar dependências (sem --system, ele criará um .venv em /app/.venv)
RUN uv sync --frozen --no-install-project

# 3. Copiar o resto do código
COPY . .

# 4. Finalizar a instalação do projeto
RUN uv sync --frozen

# 5. Adicionar o ambiente virtual ao PATH
# Isso faz com que 'fastapi', 'alembic', etc. fiquem disponíveis
ENV PATH="/app/.venv/bin:$PATH"

# Comando para iniciar
# Note que usamos 'app.main:app' (padrão de módulo) ou o caminho do arquivo
CMD ["fastapi", "run", "app/main.py", "--port", "8000", "--host", "0.0.0.0"]