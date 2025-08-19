import uuid
import logging
from sqlmodel.ext.asyncio.session import AsyncSession

from app.src.astroprofile.models import AstroProfileResponse
from app.src.birthprofile.models import BirthProfileResponse
from app.src.interpretation.datastore.implementation import InterpretationImplementation
from app.src.interpretation.models import InterpretationCreate, InterpretationResponse
from app.src.llmchat.service import LLMChatService

logger = logging.getLogger(__name__)


class InterpretationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def set_interpretation(
        self,
        birth_profile_id: uuid.UUID,
        birth_profile: BirthProfileResponse,
        astro_profile: AstroProfileResponse,
    ) -> InterpretationResponse:
        content = await LLMChatService().get_astro_interpretation(
            birth_profile, astro_profile
        )
        interpretation_data = {"birth_profile_id": birth_profile_id, "content": content}

        interpretation_model = InterpretationCreate.model_validate(interpretation_data)
        interpretation_created = await InterpretationImplementation(
            self.session
        ).create_interpretation(birth_profile_id, interpretation_model)
        logger.info(
            "Setting interpretation data",
            extra={
                "extra_info": {
                    "interpretation_data": interpretation_created.model_dump_json()
                }
            },
        )
        return interpretation_created

    async def get_interpretation(
        self, birth_profile_id: uuid.UUID
    ) -> InterpretationResponse:
        interpretation = await InterpretationImplementation(
            self.session
        ).fetch_interpretation(birth_profile_id)
        logger.info(
            "Getting Interpretation detail",
            extra={
                "extra_info": {
                    "birth_profile_id": str(birth_profile_id),
                    "interpretation_data": interpretation.model_dump_json(),
                }
            },
        )
        return interpretation

    async def remove_interpretation(self, birth_profile_id: uuid.UUID) -> None:
        logger.info(
            "Removing interpretation",
            extra={"extra_info": {"profile_id": str(birth_profile_id)}},
        )
        return await InterpretationImplementation(self.session).delete_interpretation(
            birth_profile_id
        )
