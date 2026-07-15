from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class TaskStatus(str, enum.Enum):
    backlog = "backlog"
    todo = "todo"
    in_progress = "in_progress"
    review = "review"
    done = "done"


class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.backlog, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.medium, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)