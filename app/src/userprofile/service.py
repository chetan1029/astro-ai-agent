import logging

from sqlmodel.ext.asyncio.session import AsyncSession

from app.src.userprofile.datastore.implementation import UserProfileImplementation
from app.src.userprofile.exceptions import UserProfileNotFoundError
from app.src.userprofile.models import UserProfileResponse, UserProfileCreate

logger = logging.getLogger(__name__)

class UserProfileService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def set_user_profile(self, user_profile: UserProfileCreate) -> UserProfileResponse:
        user_profile_ceated = await UserProfileImplementation(self.session).create_user_profile(user_profile)
        logger.info(
            "Setting user profile",
            extra={
                "extra_info": {"user_data": user_profile_ceated.model_dump_json()}
            },
        )
        return user_profile_ceated

    async def get_user_profile(self, phone_number: str) -> UserProfileResponse:
        user_profile = await UserProfileImplementation(
            self.session
        ).fetch_user_profile(phone_number)

        logger.info(
            "Getting user profile",
            extra={
                "extra_info": {
                    "phone_number": str(phone_number),
                    "profile_data": user_profile.model_dump_json(),
                }
            },
        )
        return user_profile

    async def remove_user_profile(self, phone_number: str) -> None:
        logger.info(
            "Removing user profile",
            extra={"extra_info": {"profile_id": str(phone_number)}},
        )
        return await UserProfileImplementation(self.session).delete_user_profile(
            phone_number
        )

    async def get_or_set_by_phone(self, phone_number: str) -> UserProfileResponse:
        try:
            return await self.get_user_profile(phone_number)
        except UserProfileNotFoundError:
            user_profile = UserProfileCreate(
                phone_number=phone_number
            )
            return await self.set_user_profile(user_profile)
