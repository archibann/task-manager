from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.enums import PriorityEnum

class TaskCreate(BaseModel):
    title: str
    deadline: Optional[date] = None
    priority: Optional[PriorityEnum] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    deadline: Optional[date]
    priority: Optional[PriorityEnum]
    completed: bool

    class Config:
        from_attributes = True

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    deadline: Optional[date] = None
    priority: Optional[PriorityEnum] = None

