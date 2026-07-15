from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.dependencies import get_current_user, get_admin_user
from app.models.user import User
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/admin/all", response_model=list[TaskOut])
async def admin_get_all_tasks(
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_admin_user),
):
    """Все задачи всех пользователей (только для админа)."""
    repo = TaskRepository(session)
    return await repo.get_all()


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    repo = TaskRepository(session)
    return await repo.create(task_data, owner_id=current_user.id)


@router.get("", response_model=list[TaskOut])
async def get_my_tasks(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    repo = TaskRepository(session)
    return await repo.get_by_owner(current_user.id)


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    repo = TaskRepository(session)
    task = await repo.get_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    if task.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Нет доступа к этой задаче")
    return task


@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    repo = TaskRepository(session)
    task = await repo.get_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    if task.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Нет доступа к этой задаче")
    return await repo.update(task, task_data)


@router.patch("/{task_id}/status", response_model=TaskOut)
async def change_status(
    task_id: int,
    new_status: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    from app.models.task import TaskStatus
    try:
        s = TaskStatus(new_status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Неверный статус: {new_status}")
    repo = TaskRepository(session)
    task = await repo.get_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    if task.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Нет доступа к этой задаче")
    return await repo.update_status(task, s)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    repo = TaskRepository(session)
    task = await repo.get_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    if task.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Нет доступа к этой задаче")
    await repo.delete(task)