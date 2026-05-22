import uvicorn
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

app = FastAPI()

DATABASE_URL = "sqlite+aiosqlite:///./testik.sqlite"
engine = create_async_engine(
    DATABASE_URL
)
new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserOut(BaseModel):
        id: int
        username: str
        email: str

        class Config:
            from_attributes = True

@app.post("/setup_database")
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        return {"ok" : True}

@app.post("/users", response_model=UserOut)
async def add_user(user: UserCreate, session: AsyncSession = Depends(get_session)):

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=user.password
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


@app.get("/users", response_model=list[UserOut])
async def get_users(session: AsyncSession = Depends(get_session)):

    result = await session.execute(select(User))
    users = result.scalars().all()

    return users

if __name__ == "__main__":
    uvicorn.run('main:app')

