import uuid
import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.birthprofile.datastore.dbmodels import BirthProfile
from app.src.birthprofile.datastore.interface import BirthProfileDataStore
from app.src.birthprofile.exceptions import BirthProfileNotFoundError, DataStoreError
from app.src.birthprofile.models import BirthProfileCreate, BirthProfileResponse

logger = logging.getLogger(__name__)


class BirthProfileImplementation(BirthProfileDataStore):
    def __init__(self, session: AsyncSession) -> None:
        logger.info(f"Initializing BirthProfileImplementation with session {session}")
        self.session = session

    async def create_birth_profile(
        self, birth_profile: BirthProfileCreate
    ) -> BirthProfileResponse:
        try:
            birth_profile_db = BirthProfile(**birth_profile.model_dump())
            self.session.add(birth_profile_db)
            await self.session.commit()
            await self.session.refresh(birth_profile_db)

            logger.info(
                "Successfully created birth profile with ID: {}".format(
                    birth_profile_db.id
                )
            )
            return BirthProfileResponse.model_validate(birth_profile_db)

        except SQLAlchemyError as db_error:
            logger.exception("Database error occurred while creating birth profile")
            await self.session.rollback()
            raise DataStoreError("Failed to create birth profile") from db_error

        except Exception as e:
            logger.exception("Unexpected error while creating birth profile")
            raise DataStoreError("Unexpected error occurred") from e

    async def fetch_birth_profile(
        self, birth_profile_id: uuid.UUID
    ) -> BirthProfileResponse:
        try:
            birth_profile = await self.session.get(BirthProfile, birth_profile_id)
        except SQLAlchemyError as db_error:
            logger.exception(
                "Database error occurred while fetching birth profile with ID: {}".format(
                    birth_profile_id
                )
            )
            await self.session.rollback()
            raise DataStoreError("Failed to fetch birth profile") from db_error

        if not birth_profile:
            raise BirthProfileNotFoundError(
                "BirthProfile not found with profile ID: {}".format(birth_profile_id)
            )

        try:
            return BirthProfileResponse.model_validate(birth_profile)
        except Exception as e:
            logger.exception(
                "Unexpected error while fetching birth profile with ID: {}".format(
                    birth_profile_id
                )
            )
            raise DataStoreError("Unexpected error occurred") from e

    async def delete_birth_profile(self, birth_profile_id: uuid.UUID) -> None:
        try:
            birth_profile = await self.session.get(BirthProfile, birth_profile_id)
            if not birth_profile:
                raise BirthProfileNotFoundError(
                    "BirthProfile not found with profile id: {}".format(
                        birth_profile_id
                    )
                )

            await self.session.delete(birth_profile)
            await self.session.commit()

        except SQLAlchemyError as db_error:
            logger.error(
                "SQLAlchemy error while deleting profile {}: {}".format(
                    birth_profile_id, str(db_error)
                ),
                exc_info=True,
            )
            await self.session.rollback()
            raise DataStoreError(
                "Failed to delete profile with ID: {}".format(birth_profile_id)
            ) from db_error

        except Exception as e:
            await self.session.rollback()
            logger.exception(
                "Unexpected error while deleting profile ID: {}".format(
                    birth_profile_id
                )
            )
            raise DataStoreError("Unexpected error occurred") from e
