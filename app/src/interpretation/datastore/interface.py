import uuid
from typing import Protocol

from app.src.interpretation.models import InterpretationCreate, InterpretationResponse


class InterpretationDataStore(Protocol):
    async def create_interpretation(self, birth_profile_id: uuid.UUID, interpretation: InterpretationCreate) -> InterpretationResponse: ...
    async def fetch_interpretation(self, birth_profile_id: uuid.UUID) -> InterpretationResponse | None: ...
    async def delete_interpretation(self, birth_profile_id: uuid.UUID) -> None: ...