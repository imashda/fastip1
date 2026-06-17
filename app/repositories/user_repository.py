from typing import Optional

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.logging_config import logger
from app.models.user import User
from app.schemas.user import UserCreate


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


class UserRepository:
    """
    Репозиторий для работы с пользователями в БД.
    Содержит все CRUD-операции и логирует каждую из них.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_data: UserCreate) -> User:
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
        )
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        logger.info(f"Создан пользователь: id={new_user.id}, username={new_user.username}")
        return new_user

    async def get_all(self) -> list[User]:
        result = await self.session.execute(select(User))
        users = list(result.scalars().all())
        logger.info(f"Запрошен список пользователей, найдено: {len(users)}")
        return users

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            logger.warning(f"Пользователь с id={user_id} не найден")
        return user

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def update(
        self,
        user_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
    ) -> Optional[User]:
        user = await self.get_by_id(user_id)
        if user is None:
            return None

        if username is not None:
            user.username = username
        if email is not None:
            user.email = email
        if password is not None:
            user.hashed_password = hash_password(password)

        await self.session.commit()
        await self.session.refresh(user)
        logger.info(f"Обновлён пользователь: id={user.id}")
        return user

    async def delete(self, user_id: int) -> bool:
        user = await self.get_by_id(user_id)
        if user is None:
            return False

        await self.session.delete(user)
        await self.session.commit()
        logger.info(f"Удалён пользователь: id={user_id}, username={user.username}")
        return True
