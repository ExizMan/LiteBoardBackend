import enum
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Enum as SqlEnum

from db.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, select, UniqueConstraint

from common.jwt.hash import verify_password
from db.lib.mixins import TimeMixin
from db.lib.types import pk_id, utcnow





class User(Base, TimeMixin):
    __tablename__ = "user"
    user_uuid: Mapped[pk_id]
    email: Mapped[str] = mapped_column(String(255), unique=True)
    phone: Mapped[str] = mapped_column(String(255), nullable=True)
    firstname: Mapped[str] = mapped_column(String(255),nullable=True)
    middlename: Mapped[str] = mapped_column(String(255),nullable=True)
    lastname: Mapped[str] = mapped_column(String(255),nullable=True)
    password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)


    @classmethod
    async def find_by_email(cls, db: AsyncSession, email: str):
        query = select(cls).where(cls.email == email)
        result = await db.execute(query)
        return result.scalars().first()


    @classmethod
    async def authenticate(cls, db: AsyncSession, email: str, password: str):
        user = await cls.find_by_email(db=db, email=email)
        if not user or not verify_password(password, user.password):
            return False
        return user


class BlackListToken(Base):
    __tablename__ = "blacklisttokens"
    id: Mapped[pk_id]
    expire: Mapped[datetime]
    created_at: Mapped[datetime] = mapped_column(server_default=utcnow())


class Teams(Base, TimeMixin):
    __tablename__ = "teams"
    id: Mapped[pk_id]
    pool: Mapped[int] = mapped_column(default=2)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str]  = mapped_column(nullable=True)

class InviteStatus(enum.Enum):
    invited = "invited"
    accepted = "accepted"
    rejected = "rejected"


class UserTeams(Base, TimeMixin):

    __tablename__ = "user_teams"
    id: Mapped[pk_id]
    user_id: Mapped[pk_id] = mapped_column(nullable=False)
    team_id: Mapped[pk_id] = mapped_column(nullable=False)
    status: Mapped[InviteStatus] = mapped_column(SqlEnum(InviteStatus), default=InviteStatus.invited)


    __table_args__ = (UniqueConstraint("user_id", "team_id"),)
    