import sys
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.logging_config import logger

# Если SECRET_KEY не задан — приложение не должно запускаться
if not SECRET_KEY or SECRET_KEY == "fallback-secret-key-not-safe":
    logger.critical("SECRET_KEY не задан или небезопасен! Задайте его в .env файле.")
    sys.exit(1)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    from datetime import datetime, timedelta, timezone
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        logger.warning("Получен недействительный или просроченный токен")
        return None