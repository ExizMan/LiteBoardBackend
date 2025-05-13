from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel
from uuid import UUID
from enum import Enum

class Role(str, Enum):
    owner = "owner"
    editor = "editor"
    viewer = "viewer"

class ParticipantIn(BaseModel):
    board_id: UUID
    user_id: UUID
    role: Role

class ParticipantOut(ParticipantIn):
    pass