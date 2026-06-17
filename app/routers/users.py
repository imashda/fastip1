from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.dependencies import get_current_user
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdate, UserOut

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserOut])
async def get_all_users(session: AsyncSession = Depends(get_session)):
    """Получить список всех пользователей."""
    repo = UserRepository(session)
    return await repo.get_all()


@router.get("/me", response_model=UserOut)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Получить профиль текущего авторизованного пользователя."""
    return current_user


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Получить пользователя по ID."""
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с id={user_id} не найден",
        )
    return user


@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Обновить свои данные. Менять можно только себя."""
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Можно редактировать только свой профиль",
        )

    repo = UserRepository(session)
    updated = await repo.update(
        user_id=user_id,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
    )
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с id={user_id} не найден",
        )
    return updated


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Удалить пользователя. Удалить можно только себя (или админ — кого угодно)."""
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Можно удалить только свой профиль",
        )

    repo = UserRepository(session)
    deleted = await repo.delete(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с id={user_id} не найден",
        )
