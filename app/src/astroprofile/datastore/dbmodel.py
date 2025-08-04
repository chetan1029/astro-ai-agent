import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field, JSON, Column


class AstroProfile(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("birth_profile_id"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    birth_profile_id: uuid.UUID = Field(
        foreign_key="birthprofile.id", index=True, unique=True
    )
    ascendant: float
    moon_nakshatra: str
    nakshatra_ruler: str
    planet_positions: dict = Field(sa_column=Column(JSON))
    houses: list = Field(sa_column=Column(JSON))
    vimshottari_dasha: dict = Field(sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
