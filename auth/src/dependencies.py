from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.users import User
from common.jwt.jwt import decode_access_token, SUB, oauth2_scheme
from db.database import get_db

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: AsyncSession = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = await decode_access_token(token, db=db)
        expr = (User.user_uuid == payload[SUB])
        user = await User.find_by_expr(db=db, expr=expr)
        if user is None:
            raise credentials_exception
    except (JWTError, ValidationError):
        raise credentials_exception
    return user
