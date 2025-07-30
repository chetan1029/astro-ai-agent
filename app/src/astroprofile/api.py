import uuid

from fastapi import APIRouter, Depends, status, HTTPException

from app.src.astroprofile.exceptions import (
    AstroProfileNotFoundError,
    DataStoreError,
    AstroProfileAlreadyExistsError,
)
from app.src.astroprofile.models import AstroProfileResponse
from app.src.birthprofile.exceptions import BirthProfileNotFoundError
from app.src.birthprofile.service import BirthProfileService
from app.src.core.db import get_session
from app.src.astroprofile.service import AstroProfileService

router = APIRouter()


@router.get(
    "/{birth_profile_id}",
    status_code=status.HTTP_200_OK,
    response_model=AstroProfileResponse,
)
async def get_astro_profile(
    birth_profile_id: uuid.UUID, session: get_session = Depends(get_session)
):
    try:
        return await AstroProfileService(session).get_astro_profile(birth_profile_id)
    except AstroProfileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DataStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/{birth_profile_id}",
    status_code=status.HTTP_200_OK,
    response_model=AstroProfileResponse,
)
async def set_astro_profile(
    birth_profile_id: uuid.UUID, session: get_session = Depends(get_session)
):
    try:
        birth_profile = await BirthProfileService(session).get_birth_profile(
            birth_profile_id
        )
        return await AstroProfileService(session).set_astro_profile(
            birth_profile_id,
            birth_profile.date_of_birth_utc,
            birth_profile.birth_place_latitude,
            birth_profile.birth_place_longitude,
        )
    except BirthProfileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except AstroProfileAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except DataStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

@router.delete("/{birth_profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_astro_profile(
    birth_profile_id: uuid.UUID, session=Depends(get_session)
):
    try:
        return await AstroProfileService(session).remove_astro_profile(birth_profile_id)
    except AstroProfileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DataStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )