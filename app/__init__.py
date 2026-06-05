from fastapi import FastAPI

from app.database import Base, engine
from app.routers import users_router


def create_app() -> FastAPI:
    app = FastAPI(title="FastAPI Users API", version="1.0.0")

    app.include_router(users_router)

    @app.post("/setup_database", tags=["System"])
    async def setup_database():
        """Создать таблицы в БД (запустить один раз при деплое)."""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return {"ok": True}

    return app


app = create_app()
