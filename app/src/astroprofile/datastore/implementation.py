import logging
import uuid

from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.src.astroprofile.datastore.dbmodel import AstroProfile
from app.src.astroprofile.datastore.interface import AstroProfileDataStore
from app.src.astroprofile.exceptions import (
    DataStoreError,
    AstroProfileNotFoundError,
    AstroProfileAlreadyExistsError,
)
from app.src.astroprofile.models import (
    AstroProfileCreate,
    AstroProfileResponse,
)

logger = logging.getLogger(__name__)


class AstroProfileImplementation(AstroProfileDataStore):
    def __init__(self, session: AsyncSession):
        logger.info(f"Initializing AstroProfileImplementation with session {session}")
        self.session = session

    async def create_astro_profile(
        self, birth_profile_id: uuid.UUID, astro_profile: AstroProfileCreate
    ) -> AstroProfileResponse:
        try:
            astro_profile_db = AstroProfile(**astro_profile.model_dump())
            self.session.add(astro_profile_db)
            await self.session.commit()
            await self.session.refresh(astro_profile_db)

            logger.info(
                "Successfully created astro profile with ID: {}".format(
                    astro_profile_db.id
                )
            )
            return AstroProfileResponse.model_validate(astro_profile_db)

        except IntegrityError as db_error:
            logger.exception("Astro Profile already exists with profile id {}".format(birth_profile_id))
            await self.session.rollback()
            raise AstroProfileAlreadyExistsError(
                "Astro profile already exists with profile id {}".format(
                    birth_profile_id
                )
            ) from db_error

        except SQLAlchemyError as db_error:
            logger.exception("Database error occurred while creating astro profile")
            await self.session.rollback()
            raise DataStoreError("Failed to create astro profile") from db_error


    async def fetch_astro_profile(
        self, birth_profile_id: uuid.UUID
    ) -> AstroProfileResponse:
        try:
            statement = select(AstroProfile).where(
                AstroProfile.birth_profile_id == birth_profile_id
            )
            result = await self.session.execute(statement)
            astro_profile = result.scalar_one_or_none()

            if not astro_profile:
                raise AstroProfileNotFoundError(
                    "AstroProfile not found with birth profile ID: {}".format(
                        birth_profile_id
                    )
                )
            return AstroProfileResponse.model_validate(astro_profile)
        except SQLAlchemyError as db_error:
            logger.exception(
                "Database error occurred while fetching astro profile with ID: {}".format(
                    birth_profile_id
                )
            )
            await self.session.rollback()
            raise DataStoreError("Failed to fetch astro profile") from db_error

        except ValidationError as e:
            logger.exception(
                "Validation error while fetching astro profile with birth profile ID: {}".format(
                    birth_profile_id
                )
            )
            raise DataStoreError("Validation error while fetching astro profile") from e

    async def delete_astro_profile(self, birth_profile_id: uuid.UUID) -> None:
        try:
            statement = select(AstroProfile).where(
                AstroProfile.birth_profile_id == birth_profile_id
            )
            result = await self.session.execute(statement)
            astro_profile = result.scalar_one_or_none()
            if not astro_profile:
                raise AstroProfileNotFoundError(
                    "Astro Profile not found with profile id: {}".format(
                        birth_profile_id
                    )
                )

            await self.session.delete(astro_profile)
            await self.session.commit()

        except SQLAlchemyError as db_error:
            logger.error(
                "SQLAlchemy error while deleting astro profile {}: {}".format(
                    birth_profile_id, str(db_error)
                ),
                exc_info=True,
            )
            await self.session.rollback()
            raise DataStoreError(
                "Failed to delete astro profile with ID: {}".format(birth_profile_id)
            ) from db_error