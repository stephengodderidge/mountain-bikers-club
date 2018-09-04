from celery import Celery

app = Celery('tasks', backend='rpc://', broker='redis://localhost')


@app.task
def add(x, y):
    return x + y
