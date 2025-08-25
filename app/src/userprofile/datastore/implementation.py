import logging

from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.src.userprofile.datastore.dbmodels import UserProfile
from app.src.userprofile.datastore.interface import UserProfileDataStore
from app.src.userprofile.exceptions import UserProfileAlreadyExistsError, DataStoreError, UserProfileNotFoundError
from app.src.userprofile.models import UserProfileResponse, UserProfileCreate

logger = logging.getLogger(__name__)

class UserProfileImplementation(UserProfileDataStore):
    def __init__(self, session: AsyncSession) -> None:
        logger.info(f"Initializing User profile with session: {session}")
        self.session = session

    async def create_user_profile(self, userprofile: UserProfileCreate) -> UserProfileResponse:
        try:
            userprofile_db = UserProfile(**userprofile.model_dump())
            self.session.add(userprofile_db)
            await self.session.commit()
            await self.session.refresh(userprofile_db)

            logger.info(f"Created user profile with id: {userprofile_db.id}")
            return UserProfileResponse.model_validate(userprofile_db)
        except IntegrityError as db_error:
            logger.exception(f"User Profile already exists with the phone number: {userprofile.phone_number}")
            await self.session.rollback()
            raise UserProfileAlreadyExistsError(f"User Profile already exists with the phone number: {userprofile.phone_number}") from db_error
        except SQLAlchemyError as db_error:
            logger.exception(f"User Profile already exists with the phone number: {userprofile.phone_number}")
            await self.session.rollback()
            raise DataStoreError(f"Error creating user profile: {db_error}")

    async def fetch_user_profile(self, phone_number: str) -> UserProfileResponse:
        try:
            statement = select(UserProfile).where(UserProfile.phone_number == phone_number)
            result = await self.session.execute(statement)
            userprofile = result.scalar_one_or_none()

            if not userprofile:
                raise UserProfileNotFoundError(f"User profile with id: {phone_number} not found")
            return UserProfileResponse.model_validate(userprofile)
        except SQLAlchemyError as db_error:
            logger.exception(f"User Profile already exists with the phone number: {phone_number}")
            await self.session.rollback()
            raise DataStoreError("Error fetching user profile") from db_error
        except ValidationError as e:
            logger.exception(f"User Profile already exists with the phone number: {phone_number}")
            raise DataStoreError("Validation error while fetching user profile") from e

    async def delete_user_profile(self, phone_number: str) -> None:
        try:
            statement = select(UserProfile).where(UserProfile.phone_number == phone_number)
            result = await self.session.execute(statement)
            userprofile = result.scalar_one_or_none()

            if not userprofile:
                raise UserProfileNotFoundError(f"User profile with id: {phone_number} not found")

            await self.session.delete(userprofile)
            await self.session.commit()

        except SQLAlchemyError as db_error:
            logger.error(
                "SQLAlchemy error while deleting user profile {}: {}".format(
                    phone_number, str(db_error)
                ),
                exc_info=True,
            )
            await self.session.rollback()
            raise DataStoreError(
                "Failed to delete user profile with ID: {}".format(phone_number)
            ) from db_error