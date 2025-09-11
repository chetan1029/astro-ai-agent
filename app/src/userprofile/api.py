import uuid

from fastapi import APIRouter, status, Depends, HTTPException

from app.src.core.db import get_session
from app.src.userprofile.exceptions import (
    DataStoreError,
    UserProfileNotFoundError,
    UserProfileAlreadyExistsError,
)
from app.src.userprofile.models import UserProfileCreate, UserProfileResponse
from app.src.userprofile.service import UserProfileService

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def set_user_profile(
    user_profile: UserProfileCreate, session: get_session = Depends(get_session)
):
    try:
        return await UserProfileService(session).set_user_profile(user_profile)
    except UserProfileAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except DataStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/{phone_number}",
    status_code=status.HTTP_200_OK,
    response_model=UserProfileResponse,
)
async def get_user_profile_by_phone_number(
    phone_number: str, session: get_session = Depends(get_session)
):
    try:
        return await UserProfileService(session).get_user_profile_by_phone_number(phone_number)
    except UserProfileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DataStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

@router.get(
    "/{user_profile_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserProfileResponse,
)
async def get_user_profile(
    user_profile_id: uuid.UUID, session: get_session = Depends(get_session)
):
    try:
        return await UserProfileService(session).get_user_profile(user_profile_id)
    except UserProfileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DataStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete("/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_profile(
    phone_number: str, session: get_session = Depends(get_session)
):
    try:
        return await UserProfileService(session).remove_user_profile(phone_number)
    except UserProfileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DataStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
