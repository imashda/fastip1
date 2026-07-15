from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.logging_config import logger
from app.models.task import Task, TaskStatus, TaskPriority
from app.schemas.task import TaskCreate


class TaskRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, task_data: TaskCreate, owner_id: int) -> Task:
        task = Task(
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            owner_id=owner_id,
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        logger.info(f"Создана задача: id={task.id}, title={task.title}, owner_id={owner_id}")
        return task

    async def get_all(self) -> list[Task]:
        result = await self.session.execute(select(Task))
        return list(result.scalars().all())

    async def get_by_owner(self, owner_id: int) -> list[Task]:
        result = await self.session.execute(
            select(Task).where(Task.owner_id == owner_id)
        )
        return list(result.scalars().all())

    async def get_by_id(self, task_id: int) -> Optional[Task]:
        result = await self.session.execute(
            select(Task).where(Task.id == task_id)
        )
        return result.scalar_one_or_none()

    async def update_status(self, task: Task, status: TaskStatus) -> Task:
        task.status = status
        await self.session.commit()
        await self.session.refresh(task)
        logger.info(f"Статус задачи id={task.id} изменён на {status}")
        return task

    async def update(self, task: Task, data) -> Task:
        if data.title is not None:
            task.title = data.title
        if data.description is not None:
            task.description = data.description
        if data.status is not None:
            task.status = data.status
        if data.priority is not None:
            task.priority = data.priority
        await self.session.commit()
        await self.session.refresh(task)
        logger.info(f"Обновлена задача id={task.id}")
        return task

    async def delete(self, task: Task) -> None:
        await self.session.delete(task)
        await self.session.commit()
        logger.info(f"Удалена задача id={task.id}")