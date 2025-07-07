from celery import Celery
import time

celery_app = Celery("tasks", broker="redis://localhost:6379/0")

@celery_app.task
def async_hello(name: str):
    time.sleep(5)
    return f"Hello, {name}!"
