from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    """Создать нового пользователя."""
    repo = UserRepository(session)

    # Проверяем уникальность username и email
    if await repo.get_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким username уже существует",
        )
    if await repo.get_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует",
        )

    return await repo.create(user_data)


@router.get("", response_model=list[UserOut])
async def get_all_users(session: AsyncSession = Depends(get_session)):
    """Получить список всех пользователей."""
    repo = UserRepository(session)
    return await repo.get_all()


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
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    """Обновить данные пользователя."""
    repo = UserRepository(session)
    updated = await repo.update(
        user_id=user_id,
        username=user_data.username,
        email=user_data.email,
        hashed_password=user_data.password,
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
):
    """Удалить пользователя."""
    repo = UserRepository(session)
    deleted = await repo.delete(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с id={user_id} не найден",
        )
