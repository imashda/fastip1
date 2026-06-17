from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from app.config import DATABASE_URL
from app.logging_config import logger

engine = create_async_engine(DATABASE_URL)
new_session = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


async def get_session() -> AsyncSession:
    async with new_session() as session:
        try:
            yield session
        except Exception:
            logger.exception("Ошибка во время работы с сессией БД, делаем rollback")
            await session.rollback()
            raise
