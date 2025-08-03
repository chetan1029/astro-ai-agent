from datetime import datetime

import pytest
from httpx import AsyncClient

BASE_URL = "http://localhost:8000"
ENDPOINT = "/birth-profile/"
TOLERANCE = 1e-5


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "name",
        "date_of_birth",
        "birth_place",
        "relationship",
        "expected_lat",
        "expected_lng",
    ),
    [
        [
            "Name 1",
            "1992-01-20T12:00:00",
            "London",
            "Self",
            51.5072178,
            -0.1275862,
        ],
        [
            "Name 2",
            "1998-01-20T02:02:00",
            "Delhi, India",
            "Son",
            28.7040592,
            77.1024902,
        ],
    ],
)
async def test_create_birth_profile(
    name: str,
    date_of_birth: datetime,
    birth_place: str,
    relationship: str,
    expected_lat: float,
    expected_lng: float,
):
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(
            "/birth-profile/",
            json={
                "name": name,
                "date_of_birth": date_of_birth,
                "birth_place": birth_place,
                "relationship": relationship,
            },
        )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == name
    assert data["date_of_birth"] == date_of_birth
    assert data["birth_place"].startswith(birth_place)
    assert data["relationship"] == relationship
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

    assert abs(data["birth_place_latitude"] - expected_lat) < TOLERANCE
    assert abs(data["birth_place_longitude"] - expected_lng) < TOLERANCE


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "missing_field", ["name", "date_of_birth", "birth_place", "relationship"]
)
async def test_create_birth_profile_missing_fields(missing_field):
    payload = {
        "name": "Test",
        "date_of_birth": "1990-01-01",
        "birth_place": "Delhi",
        "relationship": "Self",
    }
    payload.pop(missing_field)

    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(ENDPOINT, json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "name",
        "date_of_birth",
        "birth_place",
        "relationship",
        "error_message",
    ),
    [
        [
            "Name 1",
            "1992-10-10",
            "London",
            "Self",
            "Value error, Time component is required in date_of_birth (e.g. 1990-01-01T14:30:00)",
        ],
        [
            "Name 2",
            "1998-01-20T02:02:00",
            "Delhi, India",
            "Invalid",
            "Input should be 'Self', 'Mother', 'Father', 'Son', 'Daughter', 'Brother', 'Sister', 'Partner' or 'Other'",
        ],
        [
            "Name 2",
            "1998-01-20T02:02:00",
            "XXXXXX",
            "Self",
            "Value error, Could not geocode address: XXXXXX",
        ],
    ],
)
async def test_attempt_to_create_birth_profile_with_invalid_input_raise_an_error(
    name: str,
    date_of_birth: datetime,
    birth_place: str,
    relationship: str,
    error_message: str,
):
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(
            "/birth-profile/",
            json={
                "name": name,
                "date_of_birth": date_of_birth,
                "birth_place": birth_place,
                "relationship": relationship,
            },
        )

    assert response.status_code == 422

    data = response.json()
    assert data["detail"][0]["msg"] == error_message
