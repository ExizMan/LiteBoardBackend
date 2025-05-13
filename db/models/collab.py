from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum, UniqueConstraint, ForeignKey
from uuid import UUID
from db.lib.mixins import TimeMixin
from db.database import Base
import enum

from db.models.boards import Board
from db.models.users import User


class Role(str, enum.Enum):
    owner = "owner"
    editor = "editor"
    viewer = "viewer"

class Participant(Base, TimeMixin):
    __tablename__ = "board_participant"
    __table_args__ = (UniqueConstraint("board_id", "user_id"), )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    board_id: Mapped[UUID] = mapped_column(ForeignKey(Board.id))
    user_id: Mapped[UUID] = mapped_column(ForeignKey(User.user_uuid))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.viewer)