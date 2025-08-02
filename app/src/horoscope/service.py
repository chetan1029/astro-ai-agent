import uuid
import logging
from datetime import datetime

from sqlmodel.ext.asyncio.session import AsyncSession

from app.src.astroprofile.models import AstroProfileResponse
from app.src.birthprofile.models import BirthProfileResponse
from app.src.horoscope.datastore.implementation import HoroscopeImplementation
from app.src.horoscope.models import HoroscopeCreate, HoroscopeResponse
from app.src.llmchat.service import LLMChatService

logger = logging.getLogger(__name__)


class HoroscopeService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def set_horoscope(
        self,
        birth_profile_id: uuid.UUID,
        birth_profile: BirthProfileResponse,
        astro_profile: AstroProfileResponse,
    ) -> HoroscopeResponse:
        today_date = datetime.today().date()
        content = await LLMChatService().get_astro_horoscope(
            today_date, birth_profile, astro_profile
        )
        horoscope_data = {
            "birth_profile_id": birth_profile_id,
            "scope_type": "daily",
            "scope_date": today_date,
            "content": content,
        }

        horoscope_model = HoroscopeCreate.model_validate(horoscope_data)
        horoscope_created = await HoroscopeImplementation(
            self.session
        ).create_horoscope(birth_profile_id, horoscope_model)
        logger.info(
            "Setting horoscope data",
            extra={
                "extra_info": {"horoscope_data": horoscope_created.model_dump_json()}
            },
        )
        return horoscope_created

    async def get_horoscope(self, birth_profile_id: uuid.UUID) -> HoroscopeResponse:
        horoscope = await HoroscopeImplementation(self.session).fetch_horoscope(
            birth_profile_id
        )
        logger.info(
            "Getting Horoscope detail",
            extra={
                "extra_info": {
                    "birth_profile_id": str(birth_profile_id),
                    "horoscope_data": horoscope.model_dump_json(),
                }
            },
        )
        return horoscope

    async def remove_horoscope(self, birth_profile_id: uuid.UUID) -> None:
        logger.info(
            "Removing Horoscope",
            extra={"extra_info": {"profile_id": str(birth_profile_id)}},
        )
        return await HoroscopeImplementation(self.session).delete_horoscope(
            birth_profile_id
        )
