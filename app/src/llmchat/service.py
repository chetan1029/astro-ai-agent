from datetime import date

from app.src.astroprofile.models import AstroProfileResponse
from app.src.birthprofile.models import BirthProfileResponse
from app.src.llmchat.logic import LLMChatLogic
from app.src.llmchat.providers.anyllm_provider import AnyllmProvider


class LLMChatService:
    def __init__(self):
        self.provider = AnyllmProvider()
        self.logic = LLMChatLogic(self.provider)

    async def get_astro_interpretation(
        self, birth_profile: BirthProfileResponse, astro_profile: AstroProfileResponse
    ) -> str:
        astro_interpretation = await self.logic.generate_astro_interpretation(
            birth_profile, astro_profile
        )
        return astro_interpretation

    async def get_astro_horoscope(
        self,
        today_date: date,
        birth_profile: BirthProfileResponse,
        astro_profile: AstroProfileResponse,
    ) -> str:
        astro_horoscope = await self.logic.generate_astro_horoscope(
            today_date, birth_profile, astro_profile
        )
        return astro_horoscope
