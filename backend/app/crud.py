from . import models, schemas
from sqlalchemy.orm import Session

def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(title=task.title, description=task.description)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks(db: Session):
    return db.query(models.Task).all()

def get_task_by_title(db: Session, title: str):
    return db.query(models.Task).filter(models.Task.title.ilike(title)).first()

def delete_task(db: Session, task_id: int):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        return None
    db.delete(task)
    db.commit()
    return task

def get_tasks_by_ids(db: Session, ids: list[int]):
    return db.query(models.Task).filter(models.Task.id.in_(ids)).all()
