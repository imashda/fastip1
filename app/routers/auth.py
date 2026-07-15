from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token
from app.database import get_session
from app.logging_config import logger
from app.repositories.user_repository import UserRepository, verify_password
from app.schemas.user import UserCreate, UserOut, Token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    repo = UserRepository(session)

    if await repo.get_by_username(user_data.username):
        logger.warning(f"Попытка регистрации с занятым username={user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким username уже существует",
        )
    if await repo.get_by_email(user_data.email):
        logger.warning(f"Попытка регистрации с занятым email={user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует",
        )

    return await repo.create(user_data)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    repo = UserRepository(session)
    user = await repo.get_by_username(form_data.username)

    if user is None or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Неудачная попытка входа: username={form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный username или пароль",
        )

    # Кладём user_id в токен, а не username
    token = create_access_token(data={"sub": str(user.id)})
    logger.info(f"Успешный вход: username={user.username}, id={user.id}")
    return Token(access_token=token)