from celery import shared_task


@shared_task
def ping_education() -> str:
    return 'education app task works'
