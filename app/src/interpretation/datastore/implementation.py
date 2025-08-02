import uuid
import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.src.interpretation.datastore.dbmodel import Interpretation
from app.src.interpretation.datastore.interface import InterpretationDataStore
from app.src.interpretation.exceptions import (
    InterpretationAlreadyExistsError,
    DataStoreError,
    InterpretationNotFoundError,
)
from app.src.interpretation.models import InterpretationCreate, InterpretationResponse

logger = logging.getLogger(__name__)


class InterpretationImplementation(InterpretationDataStore):
    def __init__(self, session: AsyncSession):
        logger.info(f"Initializing InterpretationImplementation with session {session}")
        self.session = session

    async def create_interpretation(
        self, birth_profile_id: uuid.UUID, interpretation: InterpretationCreate
    ) -> InterpretationResponse:
        try:
            interpretation_db = Interpretation(**interpretation.model_dump())
            self.session.add(interpretation_db)
            await self.session.commit()
            await self.session.refresh(interpretation_db)

            logger.info(
                "Successfully created Interpretation with ID: {}".format(
                    interpretation_db.id
                )
            )
            return InterpretationResponse.model_validate(interpretation_db)
        except IntegrityError as db_error:
            logger.exception(
                "Interpretation already exists with profile id {}".format(
                    birth_profile_id
                )
            )
            await self.session.rollback()
            raise InterpretationAlreadyExistsError(
                "Interpretation already exists with profile id {}".format(
                    birth_profile_id
                )
            ) from db_error

        except SQLAlchemyError as db_error:
            logger.exception("Database error occurred while creating interpretation")
            await self.session.rollback()
            raise DataStoreError("Failed to create interpretation") from db_error

        except Exception as e:
            logger.exception("Unexpected error while creating interpretation")
            raise DataStoreError("Unexpected error occurred") from e

    async def fetch_interpretation(
        self, birth_profile_id: uuid.UUID
    ) -> InterpretationResponse:
        try:
            statement = select(Interpretation).where(
                Interpretation.birth_profile_id == birth_profile_id
            )
            result = await self.session.execute(statement)
            interpretation = result.scalar_one_or_none()
        except SQLAlchemyError as db_error:
            logger.exception(
                "Database error occurred while fetching interpretation with ID: {}".format(
                    birth_profile_id
                )
            )
            await self.session.rollback()
            raise DataStoreError("Failed to fetch interpretation") from db_error

        if not interpretation:
            raise InterpretationNotFoundError(
                "Interpretation not found with birth profile ID: {}".format(
                    birth_profile_id
                )
            )

        try:
            return InterpretationResponse.model_validate(interpretation)
        except Exception as e:
            logger.exception(
                "Unexpected error while fetching interpretation with birth profile ID: {}".format(
                    birth_profile_id
                )
            )
            raise DataStoreError("Unexpected error occurred") from e

    async def delete_interpretation(self, birth_profile_id: uuid.UUID) -> None:
        try:
            statement = select(Interpretation).where(
                Interpretation.birth_profile_id == birth_profile_id
            )
            result = await self.session.execute(statement)
            interpretation = result.scalar_one_or_none()
            if not interpretation:
                raise InterpretationNotFoundError(
                    "Interpretation not found with profile id: {}".format(
                        birth_profile_id
                    )
                )

            await self.session.delete(interpretation)
            await self.session.commit()

        except SQLAlchemyError as db_error:
            logger.error(
                "SQLAlchemy error while deleting Interpretation {}: {}".format(
                    birth_profile_id, str(db_error)
                ),
                exc_info=True,
            )
            await self.session.rollback()
            raise DataStoreError(
                "Failed to delete astro profile with ID: {}".format(birth_profile_id)
            ) from db_error

        except Exception as e:
            await self.session.rollback()
            logger.exception(
                "Unexpected error while deleting astro profile ID: {}".format(
                    birth_profile_id
                )
            )
            raise DataStoreError("Unexpected error occurred") from e
