import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Query, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from . import crud, models
from app.schemas import TaskCreate, TaskResponse, TaskUpdate
from typing import List
from app.enums import PriorityEnum

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_task_or_404(task_id: int, db: Session) -> models.Task:
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/tasks", response_model=List[TaskResponse])
def read_tasks(
    completed: bool = Query(None),
    priority: PriorityEnum = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    return crud.get_tasks(db, completed, priority, skip, limit)


@app.post("/tasks", response_model=TaskResponse, status_code=201)
def add_task(task: TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(
        db,
        title=task.title,
        description=task.description,
        deadline=task.deadline,
        priority=task.priority
    )


@app.delete("/tasks/{task_id}", response_model=TaskResponse)
def remove_task(task_id: int, db: Session = Depends(get_db)):
    task = get_task_or_404(task_id, db)
    return crud.delete_task(db, task_id)


@app.put("/tasks/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: int, db: Session = Depends(get_db)):
    get_task_or_404(task_id, db)
    return crud.mark_complete(db, task_id)


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task_endpoint(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db)
):
    get_task_or_404(task_id, db)
    return crud.update_task(
        db,
        task_id,
        title=task_update.title,
        description=task_update.description,
        deadline=task_update.deadline,
        priority=task_update.priority
    )
