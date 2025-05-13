from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class BoardCreate(BaseModel):
    title: str
    is_public: bool = False

class BoardOut(BaseModel):
    id: UUID
    title: str
    owner_id: UUID
    created_at: datetime
    is_public: bool

    class Config:
        orm_mode = True