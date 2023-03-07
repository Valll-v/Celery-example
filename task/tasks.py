from celery_example.celery import app as celery_app
from celery import shared_task
from celery.signals import after_task_publish


@shared_task()
def calculate_metric():
    """Долгое вычисление метрики"""
    import random
    result = 0
    for i in range(10**7):
        if random.randint(0, 1):
            result += i * i
    return result


@after_task_publish.connect
def update_sent_state(sender=None, headers=None, **kwargs):
    task = celery_app.tasks.get(sender)
    backend = task.backend if task else celery_app.backend

    backend.store_result(headers['id'], None, "SENT")