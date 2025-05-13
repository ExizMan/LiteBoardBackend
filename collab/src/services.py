from db.models.collab import Participant
from collab.src.schemas import ParticipantIn
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

async def create_participant(db: AsyncSession, data: ParticipantIn):
    participant = Participant(**data.dict())
    db.add(participant)
    await db.commit()
    await db.refresh(participant)
    return participant

async def get_board_participants(db: AsyncSession, board_id):
    res = await db.execute(select(Participant).where(Participant.board_id == board_id))
    return res.scalars().all()

async def get_participant_boards(db: AsyncSession, user_id):
    res = await db.execute(select(Participant).where(Participant.user_id == user_id))
    return res.scalars().all()