import uuid
import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.src.astroprofile.datastore.implementation import AstroProfileImplementation
from app.src.astroprofile.logic import AstroProfileLogic
from app.src.astroprofile.models import (
    AstroProfileResponse,
    AstroProfileCreate,
)

logger = logging.getLogger(__name__)


class AstroProfileService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_astro_profile(
        self, birth_profile_id: uuid.UUID
    ) -> AstroProfileResponse:
        astro_profile = await AstroProfileImplementation(
            self.session
        ).fetch_astro_profile(birth_profile_id)
        logger.info(
            "Getting astro profile",
            extra={
                "extra_info": {
                    "birth_profile_id": str(birth_profile_id),
                    # "astro_profile_data": astro_profile.model_dump_json(),
                }
            },
        )
        return astro_profile

    async def set_astro_profile(
        self,
        birth_profile_id: uuid.UUID,
        date_of_birth_utc: datetime,
        birth_place_latitude: float,
        birth_place_longitude: float,
    ) -> AstroProfileResponse:
        raw_data = await AstroProfileLogic().get_astro_profile(
            date_of_birth_utc, birth_place_latitude, birth_place_longitude
        )

        astro_profile_data = {
            "birth_profile_id": birth_profile_id,
            **raw_data,
        }

        astro_profile_model = AstroProfileCreate.model_validate(astro_profile_data)
        astro_profile_created = await AstroProfileImplementation(
            self.session
        ).create_astro_profile(birth_profile_id, astro_profile_model)
        logger.info(
            "Setting astro profile",
            extra={
                "extra_info": {
                    # "astro_profile_data": astro_profile_created.model_dump_json()
                }
            },
        )
        return astro_profile_created

    async def remove_astro_profile(self, birth_profile_id: uuid.UUID) -> None:
        logger.info(
            "Removing astro profile",
            extra={"extra_info": {"profile_id": str(birth_profile_id)}},
        )
        return await AstroProfileImplementation(self.session).delete_astro_profile(
            birth_profile_id
        )
