from celery import shared_task
import logging

@shared_task
def my_scheduled_task():
    logging.info("Scheduled task ran!")
    # Add your logic here (e.g., fetch data, update models, etc.)
    return "Task completed!"
