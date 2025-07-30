import uuid
from datetime import datetime, timezone, timedelta
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, field_validator, model_validator, confloat

from app.src.core.utils import convert_to_utc, get_lat_long_by_address


class Relationship(StrEnum):
    self = "Self"
    mother = "Mother"
    father = "Father"
    son = "Son"
    daughter = "Daughter"
    brother = "Brother"
    sister = "Sister"
    partner = "Partner"
    other = "Other"


Latitude = confloat(ge=-90.0, le=90.0)
Longitude = confloat(ge=-180.0, le=180.0)


class BirthProfile(BaseModel):
    name: str
    date_of_birth: datetime
    date_of_birth_utc: datetime | None = None
    birth_place: str
    relationship: Relationship
    birth_place_latitude: Latitude | None = None
    birth_place_longitude: Longitude | None = None

    @field_validator("date_of_birth", mode="after")
    def validate_and_normalize_dob(cls, v: datetime) -> datetime:
        v = v.astimezone(timezone.utc).replace(tzinfo=None)

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        hundred_years_ago = now - timedelta(days=365.25 * 100)

        if v < hundred_years_ago:
            raise ValueError("date_of_birth cannot be more than 100 years in the past")

        if v > now:
            raise ValueError("date_of_birth cannot be in the future")

        return v

    model_config = ConfigDict(from_attributes=True)


class BirthProfileCreate(BirthProfile):
    @model_validator(mode="after")
    def set_utc_birth_datetime_and_lat_long(self):
        # Fetch lat/long if missing
        if self.birth_place_latitude is None or self.birth_place_longitude is None:
            address, lat, lon = get_lat_long_by_address(self.birth_place)
            self.birth_place = address
            self.birth_place_latitude = lat
            self.birth_place_longitude = lon

        # Date of Birth in UTC
        self.date_of_birth_utc = convert_to_utc(
            self.date_of_birth,
            self.birth_place_latitude,
            self.birth_place_longitude,
        )
        return self


class BirthProfileResponse(BirthProfile):
    id: uuid.UUID
    date_of_birth_utc: datetime
    created_at: datetime
    updated_at: datetime
