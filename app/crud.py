from sqlalchemy.orm import Session
from .models import Task

def get_tasks(completed: bool, priority: str, db: Session):
    query = db.query(Task)
    if completed is not None:
        query = query.filter(Task.completed == completed)
    if priority is not None:
        query = query.filter(Task.priority == priority)
    return query.all()

def create_task(db: Session, title: str, deadline: str = None, priority: str =None):
    task = Task(title=title, deadline=deadline,priority=priority)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, task_id: int):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
    return task

def mark_complete(db: Session, task_id: int):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.completed = True
        db.commit()
        db.refresh(task)
    return task

def update_task (db:Session, task_id: int, title: str = None, deadline: str = None, priority: str =None):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        if title is not None:
            task.title = title
        if deadline is not None:
            task.deadline = deadline
        if priority is not None:
            task.priority = priority
        db.commit()
        db.refresh(task)
    return task
