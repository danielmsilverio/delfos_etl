import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.infra.models import table_registry


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:16', driver='psycopg') as postgres:
        _engine = create_async_engine(postgres.get_connection_url())
        yield _engine


@pytest_asyncio.fixture
async def session(engine):
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    # Provide a single session instance to tests
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    # Drop tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)
