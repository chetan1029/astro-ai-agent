from datetime import date

from app.src.astroprofile.models import AstroProfileResponse
from app.src.birthprofile.models import BirthProfileResponse
from app.src.llmchat.user_prompt import generate_user_interpretation_prompt, generate_user_horoscope_prompt
from app.src.llmchat.system_prompt import generate_system_interpretation_prompt, generate_system_horoscope_prompt
from app.src.llmchat.providers.anyllm_provider import AnyllmProvider


class LLMChatLogic:
    def __init__(self, llm_provider: AnyllmProvider):
        self.llm_provider = llm_provider

    async def generate_astro_interpretation(
        self, birth_profile: BirthProfileResponse, astro_profile: AstroProfileResponse
    ) -> str:
        system_prompt = await generate_system_interpretation_prompt()
        user_prompt = await generate_user_interpretation_prompt(
            birth_profile, astro_profile
        )
        message = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": user_prompt,
            },
        ]
        response = await self.llm_provider.chat_completion(message)
        return response

    async def generate_astro_horoscope(
        self, today_date: date, birth_profile: BirthProfileResponse, astro_profile: AstroProfileResponse
    ) -> str:
        system_prompt = await generate_system_horoscope_prompt()
        user_prompt = await generate_user_horoscope_prompt(
            today_date, birth_profile, astro_profile
        )
        message = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": user_prompt,
            },
        ]
        response = await self.llm_provider.chat_completion(message)
        return response
