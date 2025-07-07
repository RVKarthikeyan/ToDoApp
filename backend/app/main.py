from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from . import models, schemas, crud, chatbot, search

Base.metadata.create_all(bind=engine)

app = FastAPI()

# ✅ Allow frontend to connect
origins = [
    "http://127.0.0.1:8080",
    "http://localhost:8080",
    "http://0.0.0.0:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Get all tasks (reverse order)
@app.get("/tasks", response_model=list[schemas.Task])
def read_tasks(db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db)
    return list(reversed(tasks))

# ✅ Create task manually (no duplicates)
@app.post("/tasks", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    existing = crud.get_task_by_title(db, task.title)
    if existing:
        raise HTTPException(status_code=400, detail="Task already exists")
    db_task = crud.create_task(db, task)
    search.index_task(db_task.id, db_task.title, db_task.description)
    return db_task

# ✅ Create tasks from chatbot (multiple possible)
@app.post("/chat")
def chat_task(message: str, db: Session = Depends(get_db)):
    tasks = chatbot.extract_tasks_from_text(message)  # multiple tasks now
    added = []

    for title, desc in tasks:
        existing = crud.get_task_by_title(db, title)
        if not existing:
            db_task = crud.create_task(db, schemas.TaskCreate(title=title, description=desc))
            search.index_task(db_task.id, title, desc)
            added.append(db_task)

    if not added:
        raise HTTPException(status_code=400, detail="No new tasks created")

    return {"message": f"{len(added)} task(s) created", "tasks": added}

# ✅ Delete a task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    search.delete_task(task_id)
    return {"message": "Task deleted"}

# ✅ Search tasks (Elasticsearch)
@app.get("/search", response_model=list[schemas.Task])
def search_tasks(q: str = Query(...), db: Session = Depends(get_db)):
    task_ids = search.search_tasks(q)
    return crud.get_tasks_by_ids(db, task_ids)
