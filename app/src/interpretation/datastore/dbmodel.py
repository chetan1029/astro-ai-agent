import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field


class Interpretation(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("birth_profile_id"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    birth_profile_id: uuid.UUID | None = Field(
        default=None, foreign_key="birthprofile.id", index=True, unique=True
    )
    content: str = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
