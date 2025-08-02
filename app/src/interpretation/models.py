import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Interpretation(BaseModel):
    birth_profile_id: uuid.UUID
    content: str

    model_config = ConfigDict(from_attributes=True)


class InterpretationCreate(Interpretation):
    pass


class InterpretationResponse(Interpretation):
    created_at: datetime
    updated_at: datetime
