import uuid

from fastapi import APIRouter, Depends, status, HTTPException

from app.src.astroprofile.exceptions import AstroProfileNotFoundError
from app.src.birthprofile.exceptions import BirthProfileNotFoundError
from app.src.birthprofile.service import BirthProfileService
from app.src.core.db import get_session
from app.src.astroprofile.service import AstroProfileService
from app.src.horoscope.exceptions import (
    HoroscopeNotFoundError,
    HoroscopeAlreadyExistsError,
    DataStoreError,
)
from app.src.horoscope.models import HoroscopeResponse
from app.src.horoscope.service import HoroscopeService

router = APIRouter()


@router.get(
    "/{birth_profile_id}",
    status_code=status.HTTP_200_OK,
    response_model=HoroscopeResponse,
)
async def get_horoscope(
    birth_profile_id: uuid.UUID, session: get_session = Depends(get_session)
):
    try:
        return await HoroscopeService(session).get_horoscope(birth_profile_id)
    except HoroscopeNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DataStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/{birth_profile_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=HoroscopeResponse,
)
async def set_horoscope(
    birth_profile_id: uuid.UUID, session: get_session = Depends(get_session)
):
    try:
        return await HoroscopeService(session).get_horoscope(birth_profile_id)
    except HoroscopeNotFoundError:
        pass

    try:
        birth_profile = await BirthProfileService(session).get_birth_profile(
            birth_profile_id
        )
        astro_profile = await AstroProfileService(session).get_astro_profile(
            birth_profile_id
        )
        return await HoroscopeService(session).set_horoscope(
            birth_profile_id,
            birth_profile,
            astro_profile,
        )
    except BirthProfileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except AstroProfileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except HoroscopeAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except DataStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete("/{birth_profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_horoscope(birth_profile_id: uuid.UUID, session=Depends(get_session)):
    try:
        return await HoroscopeService(session).remove_horoscope(birth_profile_id)
    except HoroscopeNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DataStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
