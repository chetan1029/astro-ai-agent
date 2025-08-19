from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from fastapi import FastAPI

from app.src.api.v1.router import router
from app.src.core.db import init_db


@asynccontextmanager
async def lifespan(
    _: FastAPI,
) -> AsyncGenerator[None, Any]:
    await init_db()
    yield


app = FastAPI(
    title="Astro Ai Agent",
    description="Astro Ai Agent Api endpoint services",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)
