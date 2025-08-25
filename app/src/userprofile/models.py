import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserProfile(BaseModel):
    phone_number: str
    name: str | None = None

    model_config = ConfigDict(from_attributes=True)

class UserProfileCreate(UserProfile):
    pass

class UserProfileResponse(UserProfile):
    id: uuid.UUID
    created_at: datetime
    last_login: datetime
