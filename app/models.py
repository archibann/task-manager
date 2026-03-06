from sqlalchemy import Column, Integer, String, Boolean, Date, Enum as SQLEnum
from app.database import Base
from app.enums import PriorityEnum

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    deadline = Column(Date, nullable=True)
    priority = Column(SQLEnum(PriorityEnum), nullable=True)
    completed = Column(Boolean, default=False)