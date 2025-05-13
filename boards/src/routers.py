from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from common.jwt.jwt import oauth2_scheme, decode_access_token, SUB

from boards.src.schemas import BoardCreate, BoardOut
from db.database import get_db

from boards.src.services import create_board, get_boards_by_owner

router = APIRouter(prefix="/boards", tags=["boards"])

@router.post("/", response_model=BoardOut)
async def create_new_board(
    token: Annotated[str, Depends(oauth2_scheme)],
    board: BoardCreate,
    db: AsyncSession = Depends(get_db),
):
    token_payload = await decode_access_token(token, db)
    user_id = token_payload[SUB]
    return await create_board(db, board, user_id)

@router.get("/", response_model=list[BoardOut])
async def list_my_boards(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db),
):
    token_payload = await decode_access_token(token, db)
    user_id = token_payload[SUB]
    return await get_boards_by_owner(db, user_id)