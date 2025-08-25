import uuid
from datetime import datetime

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field


class BirthProfile(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_profile_id", "date_of_birth"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    user_profile_id: uuid.UUID = Field(foreign_key="userprofile.id", nullable=False)
    name: str = Field(nullable=False)
    date_of_birth: datetime = Field(nullable=False)
    date_of_birth_utc: datetime = Field(nullable=False)
    birth_place: str = Field(nullable=False)
    birth_place_latitude: float = Field(nullable=False)
    birth_place_longitude: float = Field(nullable=False)
    relationship: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
