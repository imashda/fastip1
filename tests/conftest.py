import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app import app
from app.database import Base, get_session

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.sqlite"

test_engine = create_async_engine(TEST_DATABASE_URL)
test_session = async_sessionmaker(test_engine, expire_on_commit=False)


async def override_get_session():
    async with test_session() as session:
        yield session


@pytest.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()