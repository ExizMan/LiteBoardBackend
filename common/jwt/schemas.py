
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, PositiveInt, field_validator, EmailStr, UUID4, Field




class UserBase(BaseModel):
    email: EmailStr
    phone: str | None = None
    firstname: str | None = None
    middlename: str | None = None
    lastname: str | None = None
    password: str | None = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    user_uuid: UUID4
    class Config:
        orm_mode = True
        from_attributes = True



class UserRegister(UserBase):
    password: str
    # confirm_password: str = Field(alias="repeatPassword")
    class Config:
        orm_mode = True
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        orm_mode = True
        from_attributes = True


class JwtTokenSchema(BaseModel):
    token: str
    payload: dict
    expire: datetime

    class Config:
        orm_mode = True
        from_attributes = True



class TokenPair(BaseModel):
    access: JwtTokenSchema
    refresh: JwtTokenSchema

    class Config:
        orm_mode = True
        from_attributes = True




class RefreshToken(BaseModel):
    refresh: str

    class Config:
        orm_mode = True
        from_attributes = True

class AccessToken(BaseModel):
    access: str

    class Config:
        orm_mode = True
        from_attributes = True
class SuccessResponseScheme(BaseModel):
    msg: str

    class Config:
        orm_mode = True
        from_attributes = True


class BlackListToken(BaseModel):
    id: UUID4
    expire: datetime




class TeamCreate(BaseModel):
    name: str
    description: str | None = None
    pool: int = 2

class InviteUser(BaseModel):
    email: str

class UpdateInviteStatus(BaseModel):
    team_id: int
    status: Literal["accepted", "rejected"]