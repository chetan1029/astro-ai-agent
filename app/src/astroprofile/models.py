import uuid
from pydantic import BaseModel, ConfigDict


class AstroProfile(BaseModel):
    birth_profile_id: uuid.UUID
    ascendant: float
    moon_nakshatra: str
    nakshatra_ruler: str
    planet_positions: dict
    houses: list
    vimshottari_dasha: dict

    model_config = ConfigDict(from_attributes=True)

class AstroProfileCreate(AstroProfile):
    pass

class AstroProfileResponse(AstroProfile):
    pass