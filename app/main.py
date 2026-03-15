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

@app.get("/")
def home(request:Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/tasks", response_model=List[TaskResponse])
def read_tasks(
    completed: bool = Query(None),
    priority: PriorityEnum=Query(None),
    db: Session = Depends(get_db)
):
    return crud.get_tasks(completed, priority, db)

@app.post("/tasks", response_model=TaskResponse)
def add_task(task: TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, task.title, task.deadline,task.priority)

@app.delete("/tasks/{task_id}",response_model=TaskResponse)
def remove_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.delete_task(db,task_id)
    if not task:
        raise HTTPException(status_code=404,detail="Task not found")
    return task

@app.put("/tasks/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.mark_complete(db, task_id)
    if not task:
        raise HTTPException(status_code=404,detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def refresh_task(task: TaskUpdate, task_id: int, db: Session = Depends(get_db)):
    task = crud.update_task(db, task_id, task.title,task.deadline,task.priority)
    if not task:
        raise HTTPException(status_code=404,detail="Task not found")
    return task