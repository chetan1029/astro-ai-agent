import uuid
from typing import Protocol

from app.src.horoscope.models import HoroscopeCreate, HoroscopeResponse


class HoroscopeDataStore(Protocol):
    async def create_horoscope(self, birth_profile_id: uuid.UUID, horoscope: HoroscopeCreate) -> HoroscopeResponse: ...
    async def fetch_horoscope(self, birth_profile_id: uuid.UUID) -> HoroscopeResponse | None: ...
    async def delete_horoscope(self, birth_profile_id: uuid.UUID) -> None: ...