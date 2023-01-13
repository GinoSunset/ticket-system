from ticsys import celery_app
from ticket.handlers import save_tickets_from_emails
import logging


from django.conf import settings


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    period_check_email = settings.PERIOD_CHECK_EMAIL
    sender.add_periodic_task(
        period_check_email, add_new_tickets_in_email.s(), name=f"check email every"
    )
    logging.info(f"Add periodic task check email every {period_check_email} seconds")


@celery_app.task
def add_new_tickets_in_email():
    logging.info("Start check email")
    count_success_emails = save_tickets_from_emails()
    logging.info(f"Success check email. Count new tickets: {count_success_emails}")
    return count_success_emails
