import uuid
from datetime import datetime

from httpx import AsyncClient


async def create_birth_profile(
    base_url: str,
    name: str,
    date_of_birth: datetime,
    birth_place: str,
    relationship: str,
) -> uuid.UUID:
    async with AsyncClient(base_url=base_url) as client:
        response = await client.post(
            "/birth-profile/",
            json={
                "name": name,
                "date_of_birth": date_of_birth,
                "birth_place": birth_place,
                "relationship": relationship,
            },
        )
    data = response.json()
    return data["id"]
