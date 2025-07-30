import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field


class BirthProfile(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    name: str = Field(nullable=False)
    date_of_birth: datetime = Field(nullable=False)
    date_of_birth_utc: datetime = Field(nullable=False)
    birth_place: str = Field(nullable=False)
    birth_place_latitude: float = Field(nullable=False)
    birth_place_longitude: float = Field(nullable=False)
    relationship: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
