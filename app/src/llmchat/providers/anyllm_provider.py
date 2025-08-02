from any_llm import acompletion

from app.src.core.config import get_settings
from app.src.llmchat.interface import LLMChatInterface


class AnyllmProvider(LLMChatInterface):
    def __init__(self):
        self.model = get_settings().anyllm_model_url

    async def chat_completion(self, message: list[dict[str, str]]) -> str:
        response = await acompletion(model=self.model, messages=message)
        return response.choices[0].message.content
