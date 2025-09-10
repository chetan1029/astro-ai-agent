import uuid
from typing import List

from fastapi import APIRouter, Depends, status, HTTPException

from app.src.birthprofile.exceptions import (
    BirthProfileNotFoundError,
    DataStoreError,
    BirthProfileAlreadyExistsError,
)
from app.src.birthprofile.models import BirthProfileResponse, BirthProfileCreate
from app.src.birthprofile.service import BirthProfileService
from app.src.core.db import get_session
from app.src.userprofile.service import UserProfileService

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def set_birth_profile(
    phone_number: str,
    birth_profile: BirthProfileCreate,
    session: get_session = Depends(get_session),
):
    try:
        user_profile = await UserProfileService(session).get_or_set_by_phone(
            phone_number
        )
        birth_profile.user_profile_id = user_profile.id
        return await BirthProfileService(session).set_birth_profile(birth_profile)
    except BirthProfileAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except DataStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/{phone_number}",
    status_code=status.HTTP_200_OK,
    response_model=List[BirthProfileResponse],
)
async def get_all_birth_profile(
    phone_number: str, session: get_session = Depends(get_session)
):
    try:
        return await BirthProfileService(session).get_all_birth_profiles(phone_number)
    except DataStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/{birth_profile_id}",
    status_code=status.HTTP_200_OK,
    response_model=BirthProfileResponse,
)
async def get_birth_profile(
    birth_profile_id: uuid.UUID, session: get_session = Depends(get_session)
):
    try:
        return await BirthProfileService(session).get_birth_profile(birth_profile_id)
    except BirthProfileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DataStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete("/{birth_profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_birth_profile(
    birth_profile_id: uuid.UUID, session=Depends(get_session)
):
    try:
        return await BirthProfileService(session).remove_birth_profile(birth_profile_id)
    except BirthProfileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DataStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
