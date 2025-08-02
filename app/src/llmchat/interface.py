from typing import Protocol


class LLMChatInterface(Protocol):
    async def chat_completion(self, message: list[dict[str, str]]) -> str: ...
