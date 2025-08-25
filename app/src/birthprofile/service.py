import uuid
import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.src.birthprofile.datastore.implementation import BirthProfileImplementation
from app.src.birthprofile.models import BirthProfileResponse, BirthProfileCreate

logger = logging.getLogger(__name__)


class BirthProfileService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_birth_profile(
        self, birth_profile_id: uuid.UUID
    ) -> BirthProfileResponse:
        birth_profile = await BirthProfileImplementation(
            self.session
        ).fetch_birth_profile(birth_profile_id)

        logger.info(
            "Getting birth profile",
            extra={
                "extra_info": {
                    "birth_profile_id": str(birth_profile_id),
                    "profile_data": birth_profile.model_dump_json(),
                }
            },
        )
        return birth_profile

    async def get_all_birth_profiles(self, phone_number: str) -> List[BirthProfileResponse]:
        birth_profiles = await BirthProfileImplementation(self.session).fetch_all_birth_profiles(phone_number)
        logger.info(
            "Getting all birth profiles",
            extra={
                "extra_info": {
                    "phone_number": phone_number,
                    "birth_profiles": birth_profiles,
                }
            }
        )
        return birth_profiles

    async def set_birth_profile(
        self, birth_profile: BirthProfileCreate
    ) -> BirthProfileResponse:
        birth_profile_created = await BirthProfileImplementation(
            self.session
        ).create_birth_profile(birth_profile)
        logger.info(
            "Setting birth profile",
            extra={
                "extra_info": {"profile_data": birth_profile_created.model_dump_json()}
            },
        )
        return birth_profile_created

    async def remove_birth_profile(self, birth_profile_id: uuid.UUID) -> None:
        logger.info(
            "Removing birth profile",
            extra={"extra_info": {"profile_id": str(birth_profile_id)}},
        )
        return await BirthProfileImplementation(self.session).delete_birth_profile(
            birth_profile_id
        )
