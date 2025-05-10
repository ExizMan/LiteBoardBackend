import os
import uuid
from datetime import timedelta, datetime, timezone

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession


from common.jwt.schemas import User, TokenPair, JwtTokenSchema
from common.exceptions import AuthFailedException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "secretkey",
)
if not SECRET_KEY:
    SECRET_KEY = os.urandom(32)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 120
REFRESH_TOKEN_EXPIRES_MINUTES = 15 * 24 * 60  # 15 days

REFRESH_COOKIE_NAME = "refresh"
SUB = "sub"
EXP = "exp"
IAT = "iat"
JTI = "jti"


def _create_access_token(payload: dict, minutes: int | None = None) -> JwtTokenSchema:
    expire = datetime.utcnow() + timedelta(
        minutes=minutes or ACCESS_TOKEN_EXPIRES_MINUTES
    )

    payload[EXP] = expire

    token = JwtTokenSchema(
        token=jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM),
        payload=payload,
        expire=expire,
    )

    return token


def _create_refresh_token(payload: dict) -> JwtTokenSchema:
    expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRES_MINUTES)

    payload[EXP] = expire

    token = JwtTokenSchema(
        token=jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM),
        expire=expire,
        payload=payload,
    )

    return token


def create_token_pair(user: User) -> TokenPair:
    payload = {SUB: str(user.user_uuid), JTI: str(uuid.uuid4()), IAT: datetime.utcnow()}

    return TokenPair(
        access=_create_access_token(payload={**payload}),
        refresh=_create_refresh_token(payload={**payload}),
    )


async def decode_access_token(token: str, db: AsyncSession):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # black_list_token = await BlackListToken.find_by_id(db=db, id=payload[JTI])
        # if black_list_token:
        #     raise JWTError("Token is blacklisted")
    except JWTError as ex:
        print(str(ex))
        raise AuthFailedException()

    return payload


def refresh_token_state(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as ex:
        print(str(ex))
        raise AuthFailedException()

    return {"token": _create_access_token(payload=payload).token}


def mail_token(user: User):
    """Return 2 hour lifetime access_token"""
    payload = {SUB: str(user.user_uuid), JTI: str(uuid.uuid4()), IAT: datetime.utcnow()}
    return _create_access_token(payload=payload, minutes=2 * 60).token


def add_refresh_token_cookie(response: Response, token: str):
    exp = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRES_MINUTES)
    exp.replace(tzinfo=timezone.utc)

    response.set_cookie(
        key="refresh",
        value=token,
        expires=int(exp.timestamp()),
        httponly=False,
        samesite='strict',
    )