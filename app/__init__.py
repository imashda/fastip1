import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.logging_config import logger
from app.routers import auth_router, users_router, admin_router, tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Таблицы БД проверены/созданы")
    logger.info("Приложение запущено")
    yield
    logger.info("Приложение остановлено")


def create_app() -> FastAPI:
    app = FastAPI(title="FastAPI Users API", version="2.0.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(admin_router)
    app.include_router(tasks_router)

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        try:
            response = await call_next(request)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms} ms)")
            return response
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger.exception(f"{request.method} {request.url.path} -> 500 ({duration_ms} ms) | Ошибка: {e}")
            raise

    return app


app = create_app()