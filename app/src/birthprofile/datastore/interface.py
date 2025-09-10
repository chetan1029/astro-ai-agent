import uuid
from typing import Protocol, List

from app.src.birthprofile.models import BirthProfileCreate, BirthProfileResponse


class BirthProfileDataStore(Protocol):
    async def create_birth_profile(
        self, birth_profile: BirthProfileCreate
    ) -> BirthProfileResponse: ...

    async def fetch_all_birth_profiles(
        self, phone_number: str
    ) -> List[BirthProfileResponse]: ...

    async def fetch_birth_profile(
        self, birth_profile_id: uuid.UUID
    ) -> BirthProfileResponse | None: ...

    async def delete_birth_profile(self, birth_profile_id: uuid.UUID) -> None: ...
