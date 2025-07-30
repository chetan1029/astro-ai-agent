import uuid
from typing import Protocol

from app.src.astroprofile.models import AstroProfileCreate, AstroProfileResponse


class AstroProfileDataStore(Protocol):
    async def fetch_astro_profile(self, birth_profile_id: uuid.UUID) -> AstroProfileResponse | None: ...
    async def create_astro_profile(self, birth_profile_id: uuid.UUID, astro_profile: AstroProfileCreate) -> AstroProfileResponse: ...
    async def delete_astro_profile(self, birth_profile_id: uuid.UUID) -> None: ...