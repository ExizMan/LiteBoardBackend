from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from db.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, select

from common.jwt.hash import verify_password
from db.lib.types import pk_id, created_at, updated_at, utcnow


class AttributeMixin:
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class User(Base, AttributeMixin):
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


