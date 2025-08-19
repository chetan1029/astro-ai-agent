import uuid
import logging

from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.src.horoscope.datastore.dbmodel import Horoscope
from app.src.horoscope.datastore.interface import HoroscopeDataStore
from app.src.horoscope.exceptions import (
    HoroscopeAlreadyExistsError,
    DataStoreError,
    HoroscopeNotFoundError,
)
from app.src.horoscope.models import HoroscopeCreate, HoroscopeResponse

logger = logging.getLogger(__name__)


class HoroscopeImplementation(HoroscopeDataStore):
    def __init__(self, session: AsyncSession):
        logger.info(f"Initializing HoroscopeImplementation with session {session}")
        self.session = session

    async def create_horoscope(
        self, birth_profile_id: uuid.UUID, horoscope: HoroscopeCreate
    ) -> HoroscopeResponse:
        try:
            horoscope_db = Horoscope(**horoscope.model_dump())
            self.session.add(horoscope_db)
            await self.session.commit()
            await self.session.refresh(horoscope_db)

            logger.info(
                "Successfully created Horoscope with ID: {}".format(horoscope_db.id)
            )
            return HoroscopeResponse.model_validate(horoscope_db)
        except IntegrityError as db_error:
            logger.exception(
                "Horoscope already exists with profile id {}".format(birth_profile_id)
            )
            await self.session.rollback()
            raise HoroscopeAlreadyExistsError(
                "Horoscope already exists with profile id {}".format(birth_profile_id)
            ) from db_error

        except SQLAlchemyError as db_error:
            logger.exception("Database error occurred while creating horoscope")
            await self.session.rollback()
            raise DataStoreError("Failed to create horoscope") from db_error

    async def fetch_horoscope(self, birth_profile_id: uuid.UUID) -> HoroscopeResponse:
        try:
            statement = select(Horoscope).where(
                Horoscope.birth_profile_id == birth_profile_id
            )
            result = await self.session.execute(statement)
            horoscope = result.scalar_one_or_none()

            if not horoscope:
                raise HoroscopeNotFoundError(
                    "Horoscope not found with birth profile ID: {}".format(
                        birth_profile_id
                    )
                )
            return HoroscopeResponse.model_validate(horoscope)
        except SQLAlchemyError as db_error:
            logger.exception(
                "Database error occurred while fetching horoscope with ID: {}".format(
                    birth_profile_id
                )
            )
            await self.session.rollback()
            raise DataStoreError("Failed to fetch horoscope") from db_error

        except ValidationError as e:
            logger.exception(
                "Validation error while fetching horoscope with birth profile ID: {}".format(
                    birth_profile_id
                )
            )
            raise DataStoreError("Validation error while fetching horoscope") from e

    async def delete_horoscope(self, birth_profile_id: uuid.UUID) -> None:
        try:
            statement = select(Horoscope).where(
                Horoscope.birth_profile_id == birth_profile_id
            )
            result = await self.session.execute(statement)
            horoscope = result.scalar_one_or_none()
            if not horoscope:
                raise HoroscopeNotFoundError(
                    "Horoscope not found with profile id: {}".format(birth_profile_id)
                )

            await self.session.delete(horoscope)
            await self.session.commit()

        except SQLAlchemyError as db_error:
            logger.error(
                "SQLAlchemy error while deleting Horoscope {}: {}".format(
                    birth_profile_id, str(db_error)
                ),
                exc_info=True,
            )
            await self.session.rollback()
            raise DataStoreError(
                "Failed to delete astro profile with ID: {}".format(birth_profile_id)
            ) from db_error
