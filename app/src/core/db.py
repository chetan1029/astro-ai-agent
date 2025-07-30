from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from typing import AsyncGenerator

from sqlmodel import SQLModel
from app.src.core.config import get_settings


postgres_url = get_settings().database_url
engine = create_async_engine(
    postgres_url,
    echo=True,
    future=True,
)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def init_db() -> None:
    async with engine.begin() as conn:
        from app.src.birthprofile.datastore.dbmodels import BirthProfile
        from app.src.astroprofile.datastore.dbmodel import AstroProfile

        await conn.run_sync(SQLModel.metadata.create_all)
