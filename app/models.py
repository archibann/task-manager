from sqlalchemy import Column, Integer, String, Boolean, Date, Enum as SQLEnum, DateTime
from sqlalchemy.sql import func
from app.database import Base
from app.enums import PriorityEnum

class Task(Base):
    """
    Модель задачи для управления задачами.
    
    Attributes:
        id: Уникальный идентификатор задачи
        title: Название задачи
        description: Описание задачи
        deadline: Дедлайн выполнения
        priority: Приоритет задачи
        completed: Статус выполнения
        created_at: Дата и время создания задачи
    """
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(String, nullable=True)
    deadline = Column(Date, nullable=True)
    priority = Column(SQLEnum(PriorityEnum), nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', completed={self.completed})>"
