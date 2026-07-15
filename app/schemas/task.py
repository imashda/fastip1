from pydantic import BaseModel, field_validator
from app.models.task import TaskStatus, TaskPriority


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: TaskPriority = TaskPriority.medium

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Название задачи не может быть пустым")
        return v.strip()


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None


class TaskOut(BaseModel):
    id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    owner_id: int

    class Config:
        from_attributes = True