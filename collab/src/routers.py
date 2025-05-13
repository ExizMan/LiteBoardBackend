from typing import Annotated

from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from common.jwt.jwt import oauth2_scheme, decode_access_token, SUB
from db.database import get_db
from collab.src.schemas import ParticipantIn, ParticipantOut
from collab.src.services import create_participant, get_board_participants, get_participant_boards

router = APIRouter(prefix="/collab", tags=["collaboration"])

@router.post("/add", response_model=ParticipantOut, summary="Добавить участника на доску, при добавлении указывется роль")
async def add_participant(
    token: Annotated[str, Depends(oauth2_scheme)],
    participant: ParticipantIn,
    db: AsyncSession = Depends(get_db),

):
    return await create_participant(db, participant)

@router.get("/board/{board_id}", response_model=list[ParticipantOut], summary="Получить список участников всех пользователей для доски {board_id}")
async def list_participants(
    token: Annotated[str, Depends(oauth2_scheme)],
    board_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    return await get_board_participants(db, board_id)

@router.get("/my", response_model=list[ParticipantOut], summary="Получить все доски текущего пользователя")
async def my_participations(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db),

):
    """
    Возвращает все доски, в которых участвует текущий пользователь.

    Используется, чтобы отобразить доступные доски на главной странице.
    """
    token_payload = await decode_access_token(token, db)
    user_id = token_payload[SUB]
    return await get_participant_boards(db, user_id)