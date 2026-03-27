from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date, datetime
from app.enums import PriorityEnum


class TaskCreate(BaseModel):
    """
    Схема для создания новой задачи.
    """
    title: str = Field(..., min_length=1, max_length=255, description="Название задачи")
    description: Optional[str] = Field(None, description="Описание задачи")
    deadline: Optional[date] = Field(None, description="Дедлайн выполнения")
    priority: Optional[PriorityEnum] = Field(None, description="Приоритет задачи")
    
    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Название задачи не может быть пустым')
        return v.strip()


class TaskResponse(BaseModel):
    """
    Схема для ответа с данными задачи.
    """
    id: int = Field(..., description="Уникальный идентификатор задачи")
    title: str = Field(..., description="Название задачи")
    description: Optional[str] = Field(None, description="Описание задачи")
    deadline: Optional[date] = Field(None, description="Дедлайн выполнения")
    priority: Optional[PriorityEnum] = Field(None, description="Приоритет задачи")
    completed: bool = Field(..., description="Статус выполнения")
    created_at: datetime = Field(..., description="Дата и время создания задачи")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


class TaskUpdate(BaseModel):
    """
    Схема для обновления задачи.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Новое название задачи")
    description: Optional[str] = Field(None, description="Новое описание задачи")
    deadline: Optional[date] = Field(None, description="Новый дедлайн")
    priority: Optional[PriorityEnum] = Field(None, description="Новый приоритет")
    
    @validator('title')
    def validate_title(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Название задачи не может быть пустым')
        return v.strip() if v else v

