import asyncio
import os
import traceback
from contextlib import asynccontextmanager
import uvicorn
from alembic import command
from alembic.config import Config
from fastapi import FastAPI, logger, Request
from starlette.responses import PlainTextResponse

from app.database import engine
from app.routes import router
from app.models import Base


def run_migrations():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ini_path = os.path.join(base_dir, "alembic.ini")
    alembic_cfg = Config(ini_path)
    migrations_path = os.path.join(base_dir, "app", "migrations")
    alembic_cfg.set_main_option("script_location", migrations_path)
    print(f"Applying migrations from {migrations_path}...")
    command.upgrade(alembic_cfg, "head")
    print("Done.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    print("Shutting down...")


app = FastAPI(title="Art Travel Planner API", lifespan=lifespan)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url}: {exc}")
    logger.error(traceback.format_exc())
    return PlainTextResponse(str(exc), status_code=500)


app.include_router(router, tags=["Projects"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
