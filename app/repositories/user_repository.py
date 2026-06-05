from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:
    """
    Репозиторий для работы с пользователями в БД.
    Содержит все CRUD-операции.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    # CREATE
    async def create(self, user_data: UserCreate) -> User:
        """Создать нового пользователя."""
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=user_data.password,  # TODO: хэшировать пароль
        )
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user

    # READ — все
    async def get_all(self) -> list[User]:
        """Получить список всех пользователей."""
        result = await self.session.execute(select(User))
        return list(result.scalars().all())

    # READ — по id
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID. Вернёт None если не найден."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    # READ — по username
    async def get_by_username(self, username: str) -> Optional[User]:
        """Получить пользователя по username."""
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    # READ — по email
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email."""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    # UPDATE
    async def update(
        self,
        user_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        hashed_password: Optional[str] = None,
    ) -> Optional[User]:
        """
        Обновить данные пользователя по ID.
        Передавай только те поля, которые нужно изменить.
        Вернёт None если пользователь не найден.
        """
        user = await self.get_by_id(user_id)
        if user is None:
            return None

        if username is not None:
            user.username = username
        if email is not None:
            user.email = email
        if hashed_password is not None:
            user.hashed_password = hashed_password

        await self.session.commit()
        await self.session.refresh(user)
        return user

    # DELETE
    async def delete(self, user_id: int) -> bool:
        """
        Удалить пользователя по ID.
        Вернёт True если удалён, False если не найден.
        """
        user = await self.get_by_id(user_id)
        if user is None:
            return False

        await self.session.delete(user)
        await self.session.commit()
        return True
