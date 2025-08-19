import uuid
from datetime import datetime, date
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field


class Horoscope(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "birth_profile_id", "scope_type", "scope_date", name="uq_horoscope_entry"
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    birth_profile_id: uuid.UUID = Field(foreign_key="birthprofile.id", index=True)
    scope_type: str = Field(index=True)
    scope_date: Optional[date] = Field(default=None)
    content: Optional[str] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
