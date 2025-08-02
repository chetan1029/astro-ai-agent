import uuid
from datetime import datetime, date
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class Scope(StrEnum):
    Daily = "daily"
    Weekly = "weekly"
    Monthly = "monthly"


class Horoscope(BaseModel):
    birth_profile_id: uuid.UUID
    scope_type: Scope
    scope_date: date
    content: str

    model_config = ConfigDict(from_attributes=True)


class HoroscopeCreate(Horoscope):
    pass


class HoroscopeResponse(Horoscope):
    created_at: datetime
    updated_at: datetime
