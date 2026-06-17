from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.dependencies import get_admin_user
from app.logging_config import logger
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserOut

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=list[UserOut])
async def admin_get_all_users(
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_admin_user),
):
    """Список всех пользователей (только для админа)."""
    repo = UserRepository(session)
    return await repo.get_all()


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_admin_user),
):
    """Удалить любого пользователя (только для админа)."""
    repo = UserRepository(session)
    deleted = await repo.delete(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с id={user_id} не найден",
        )


@router.put("/users/{user_id}/make-admin", response_model=UserOut)
async def make_admin(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_admin_user),
):
    """Назначить пользователя администратором (только для админа)."""
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с id={user_id} не найден",
        )
    user.is_admin = True
    await session.commit()
    await session.refresh(user)
    logger.info(f"Пользователь id={user_id} назначен администратором админом id={admin.id}")
    return user
