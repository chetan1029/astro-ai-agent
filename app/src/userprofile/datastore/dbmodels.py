import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class UserProfile(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    phone_number: str = Field(nullable=False, index=True, unique=True)
    name: Optional[str] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: datetime = Field(default_factory=datetime.now)
