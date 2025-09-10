from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from fastapi import FastAPI

from app.src.api.v1.router import router
from app.src.core.db import init_db
from app.src.core.pubsub.init_pubsub import init_pubsub


@asynccontextmanager
async def lifespan(
    _: FastAPI,
) -> AsyncGenerator[None, Any]:
    await init_db()
    # Initialize Pub/Sub (topics & subscriptions)
    # Wrap in a thread-safe executor if it’s blocking
    import asyncio

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, init_pubsub)
    yield


app = FastAPI(
    title="Astro Ai Agent",
    description="Astro Ai Agent Api endpoint services",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)
