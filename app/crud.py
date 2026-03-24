from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session
from app.models import Task
from app.enums import PriorityEnum


def get_tasks(
    db: Session,
    completed: Optional[bool] = None,
    priority: Optional[PriorityEnum] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Task]:
    query = db.query(Task)
    if completed is not None:
        query = query.filter(Task.completed == completed)
    if priority is not None:
        query = query.filter(Task.priority == priority)
    return query.offset(skip).limit(limit).all()


def create_task(
    db: Session,
    title: str,
    description: Optional[str] = None,
    deadline: Optional[date] = None,
    priority: Optional[PriorityEnum] = None
) -> Task:
    task = Task(
        title=title,
        description=description,
        deadline=deadline,
        priority=priority
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(db: Session, task_id: int) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id).first()


def delete_task(db: Session, task_id: int) -> Optional[Task]:
    task = get_task(db, task_id)
    if task:
        db.delete(task)
        db.commit()
    return task


def mark_complete(db: Session, task_id: int) -> Optional[Task]:
    task = get_task(db, task_id)
    if task:
        task.completed = True
        db.commit()
        db.refresh(task)
    return task


def update_task(
    db: Session,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    deadline: Optional[date] = None,
    priority: Optional[PriorityEnum] = None
) -> Optional[Task]:
    task = get_task(db, task_id)
    if task:
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if deadline is not None:
            task.deadline = deadline
        if priority is not None:
            task.priority = priority
        db.commit()
        db.refresh(task)
    return task
