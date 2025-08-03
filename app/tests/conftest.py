import asyncio

import pytest
from testcontainers.postgres import PostgresContainer
from app.src.core.config import Settings, get_settings
from app.src.core.db import init_db
from app.src.main import app


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def test_settings(postgres_container):
    db_url = postgres_container.get_connection_url().replace(
        "postgresql://", "postgresql+asyncpg://"
    )
    return Settings(
        postgres_user="test",  # not used, but needed for constructor
        postgres_password="test",
        postgres_db="test",
        database_host="localhost",
        database_port=5432,
        app_name="test",
        app_env="test",
        app_token="token",
        admin_email="x@example.com",
        google_api_key="fake",
        openai_api_key="fake",
        anyllm_provider="test",
        anyllm_model="test",
    )


@pytest.fixture(scope="session", autouse=True)
def initialize_test_db():
    asyncio.run(init_db())


@pytest.fixture(scope="session", autouse=True)
def override_settings(test_settings):
    def override():
        return test_settings

    app.dependency_overrides[get_settings] = override
