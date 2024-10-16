from ticsys import celery_app
from ticket.handlers import save_tickets_from_emails
from ticket.handlers_itsm import get_tasks_from_itsm, create_itsm_task
import logging


from django.conf import settings


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    logging.info("Setup periodic tasks check email")
    period_check_email = settings.PERIOD_CHECK_EMAIL
    sender.add_periodic_task(
        period_check_email, add_new_tickets_in_email.s(), name=f"check email every {period_check_email}s"
    )
    sender.add_periodic_task(
        period_check_email, add_new_tickets_in_itsm.s(), name=f"check itsm every {period_check_email}s"
    )


@celery_app.task
def add_new_tickets_in_email():
    logging.debug("Start check email")
    count_success_emails = save_tickets_from_emails()
    if count_success_emails:
        logging.info(f"Success check email. Count new tickets: {count_success_emails}")
    return count_success_emails

@celery_app.task
def add_new_tickets_in_itsm():
    logging.debug("Start check itms")
    tasks = get_tasks_from_itsm()
    logging.info(f"Success check itsm. Count new tickets: {len(tasks)}")
    for task in tasks:
        create_one_itsm_ticket.delay(task)


@celery_app.task
def create_one_itsm_ticket(ticket: dict):
    logging.debug(f"Start create itsm [{ticket.get('sys_id')}]")
    create_itsm_task(ticket)
