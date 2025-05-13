from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.models.boards import Board
from boards.src.schemas import BoardCreate
from uuid import UUID

async def create_board(db: AsyncSession, data: BoardCreate, user_id: UUID) -> Board:
    board = Board(title=data.title, is_public=data.is_public, owner_id=user_id)
    db.add(board)
    await db.commit()
    await db.refresh(board)
    return board

async def get_boards_by_owner(db: AsyncSession, user_id: UUID):
    result = await db.execute(select(Board).where(Board.owner_id == user_id))
    return result.scalars().all()