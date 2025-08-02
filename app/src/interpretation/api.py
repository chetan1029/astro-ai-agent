import uuid

from fastapi import APIRouter, Depends, status, HTTPException

from app.src.astroprofile.exceptions import AstroProfileNotFoundError
from app.src.birthprofile.exceptions import BirthProfileNotFoundError
from app.src.birthprofile.service import BirthProfileService
from app.src.core.db import get_session
from app.src.astroprofile.service import AstroProfileService
from app.src.interpretation.exceptions import (
    InterpretationNotFoundError,
    InterpretationAlreadyExistsError,
    DataStoreError,
)
from app.src.interpretation.models import InterpretationResponse
from app.src.interpretation.service import InterpretationService

router = APIRouter()


@router.get(
    "/{birth_profile_id}",
    status_code=status.HTTP_200_OK,
    response_model=InterpretationResponse,
)
async def get_interpretation(
    birth_profile_id: uuid.UUID, session: get_session = Depends(get_session)
):
    try:
        return await InterpretationService(session).get_interpretation(birth_profile_id)
    except InterpretationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DataStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/{birth_profile_id}",
    status_code=status.HTTP_200_OK,
    response_model=InterpretationResponse,
)
async def set_interpretation(
    birth_profile_id: uuid.UUID, session: get_session = Depends(get_session)
):
    try:
        return await InterpretationService(session).get_interpretation(birth_profile_id)
    except InterpretationNotFoundError:
        pass

    try:
        birth_profile = await BirthProfileService(session).get_birth_profile(
            birth_profile_id
        )
        astro_profile = await AstroProfileService(session).get_astro_profile(
            birth_profile_id
        )
        return await InterpretationService(session).set_interpretation(
            birth_profile_id,
            birth_profile,
            astro_profile,
        )
    except BirthProfileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except AstroProfileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except InterpretationAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except DataStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete("/{birth_profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_interpretation(
    birth_profile_id: uuid.UUID, session=Depends(get_session)
):
    try:
        return await InterpretationService(session).remove_interpretation(
            birth_profile_id
        )
    except InterpretationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DataStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
