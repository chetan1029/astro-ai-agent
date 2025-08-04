from datetime import datetime

import pytest
from httpx import AsyncClient

from app.tests.e2e.helper.birthprofile import create_birth_profile

BASE_URL = "http://localhost:8000"
ENDPOINT = "/astro-profile/"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "name",
        "date_of_birth",
        "birth_place",
        "relationship",
        "ascendant",
        "moon_nakshatra",
        "nakshatra_ruler",
    ),
    [
        [
            "User 1",
            "1992-01-20T12:00:00",
            "London",
            "Self",
            30,
            "Pushya",
            "Saturn",
        ],
        [
            "User 2",
            "1998-01-20T02:02:00",
            "Delhi, India",
            "Son",
            210,
            "Chitra",
            "Mars",
        ],
    ],
)
async def test_create_astro_profile(
    name: str,
    date_of_birth: datetime,
    birth_place: str,
    relationship: str,
    ascendant: int,
    moon_nakshatra: str,
    nakshatra_ruler: str,
):
    birth_profile_id = await create_birth_profile(
        base_url=BASE_URL,
        name=name,
        date_of_birth=date_of_birth,
        birth_place=birth_place,
        relationship=relationship,
    )
    print(birth_profile_id)
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(f"{ENDPOINT}{birth_profile_id}")

    assert response.status_code == 201

    data = response.json()
    assert data["ascendant"] == ascendant
    assert data["moon_nakshatra"] == moon_nakshatra
    assert data["nakshatra_ruler"] == nakshatra_ruler


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("birth_profile_id", "error_code"),
    [
        [
            123,
            422,
        ],
        [
            "c0afc121-0ad2-4441-95d9-304143ca9767",
            404,
        ],
        [
            "0ad2-4441-95d9-304143ca9767",
            422,
        ],
    ],
)
async def test_attempt_to_create_astro_profile_with_invalid_input_raise_an_error(
    birth_profile_id: str,
    error_code: int,
):
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(f"{ENDPOINT}{birth_profile_id}")

    assert response.status_code == error_code
