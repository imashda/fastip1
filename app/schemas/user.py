from pydantic import BaseModel, field_validator


class UserCreate(BaseModel):
    username: str
    email: str
    password: str

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Username не может быть пустым")
        if len(v) < 3:
            raise ValueError("Username должен содержать минимум 3 символа")
        return v.strip()

    @field_validator("email")
    @classmethod
    def email_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Email не может быть пустым")
        if "@" not in v:
            raise ValueError("Некорректный формат email")
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Пароль должен содержать минимум 6 символов")
        return v


class UserUpdate(BaseModel):
    """
    Схема для обновления — все поля опциональны.
    Позволяет менять только то что нужно, без password по умолчанию.
    """
    username: str | None = None
    email: str | None = None
    password: str | None = None

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not v.strip() or len(v) < 3:
            raise ValueError("Username должен содержать минимум 3 символа")
        return v.strip()

    @field_validator("email")
    @classmethod
    def email_valid(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if "@" not in v:
            raise ValueError("Некорректный формат email")
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def password_valid(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if len(v) < 6:
            raise ValueError("Пароль должен содержать минимум 6 символов")
        return v


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
