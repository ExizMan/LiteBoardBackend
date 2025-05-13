from sqlalchemy import String, ForeignKey, UUID
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base
from db.lib.mixins import TimeMixin
from db.lib.types import pk_id
from db.models.users import User


class Board(Base, TimeMixin):
    __tablename__ = "board"

    id: Mapped[pk_id]
    title: Mapped[str] = mapped_column(String(255))
    owner_id: Mapped[UUID] = mapped_column(ForeignKey(User.user_uuid))
    is_public: Mapped[bool] = mapped_column(default=False)
