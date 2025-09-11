import uuid
from typing import Protocol
from app.src.userprofile.models import UserProfileResponse, UserProfileCreate


class UserProfileDataStore(Protocol):
    async def create_user_profile(
        self, userprofile: UserProfileCreate
    ) -> UserProfileResponse: ...

    async def fetch_user_profile_by_phone_number(
        self, phone_number: str
    ) -> UserProfileResponse | None: ...

    async def fetch_user_profile(
        self, user_profile_id: uuid.UUID
    ) -> UserProfileResponse | None: ...

    async def delete_user_profile(self, phone_number: str) -> None: ...
