import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.infra.database.database import get_session
from app.infra.models.sensor import table_registry
from app.main import app


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


@pytest.fixture
def client(session):
    async def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()
