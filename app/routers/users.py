from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_token
from app.database import get_session
from app.dependencies import get_admin_user
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdate, UserOut

router = APIRouter(prefix="/users", tags=["Users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен недействителен или истёк",
        )
    # Теперь берём user_id из токена (не username)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Некорректный токен")
    repo = UserRepository(session)
    user = await repo.get_by_id(int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user


@router.get("/me", response_model=UserOut)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Профиль текущего пользователя."""
    return current_user