from typing import Sequence

from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.template import loader

from ticket.models import Ticket

User = get_user_model()


class Notification(models.Model):
    class TypeNotification(models.TextChoices):
        NEW_TICKET = "new_ticket", "Новая заявка"
        NEW_COMMENT = "new_comment", "Новый комментарий"
        SET_CONTRACTOR = "set_contractor", "Установлен подрядчик"
        TICKET_TO_WORK = "ticket_to_work", "Заявка в работе"
        TICKET_DONE = "ticket_done", "Заявка выполнена"
        TICKET_CANCEL = "ticket_cancel", "Заявка отменена"
        OTHER = "other", "Другое"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    email = models.EmailField(blank=True, null=True)
    emails = models.TextField(blank=True, null=True)

    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=255, blank=True, null=True)

    type_notify = models.CharField(
        "Тип оповещения",
        max_length=50,
        choices=TypeNotification.choices,
        default=TypeNotification.OTHER,
    )
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="notifications",
        blank=True,
        null=True,
    )

    def get_emails(self) -> Sequence[str]:
        emails = set()
        if self.email:
            emails.add(self.email)
        if self.user and self.user.email:
            emails.add(self.user.email)
        if self.emails:
            emails_list = [i.strip().lower() for i in self.emails.split(",")]
            emails.update(emails_list)
        self.remove_self_email(emails)
        return list(emails)

    def remove_self_email(self, emails: set):
        """
        remove email from list if it is equal to EMAIL_HOST_USER for not spamming
        """
        if settings.EMAIL_HOST_USER.lower() in emails:
            emails.remove(settings.EMAIL_HOST_USER.lower())

    def __str__(self):
        return f"{self.user} - {self.message}"

    def is_needed_to_attach_files(self):
        return self.type_notify in [Notification.TypeNotification.TICKET_DONE]

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"

    @classmethod
    def create_notify_update_ticket(cls, update_field, ticket: Ticket):
        template_dict = {
            "contractor": Notification.create_notify_update_contractor,
        }
        for field in update_field:
            create_func = template_dict.get(field)
            if create_func:
                create_func(ticket)

    @classmethod
    def create_notify_update_contractor(cls, ticket: Ticket):
        link = ticket.get_external_url()
        message = loader.get_template("notifications/notify_set_contractor.txt").render(
            {"ticket": ticket, "link": link}
        )
        user = ticket.contractor
        cls.objects.create(
            user=user,
            message=message,
            type_notify=cls.TypeNotification.SET_CONTRACTOR,
            ticket=ticket,
            subject=f"Заявка №{ticket.id}",
        )

    @classmethod
    def create_notify_for_customer_when_ticket_to_work(cls, ticket: Ticket):
        link = ticket.get_external_url()
        message = loader.get_template(
            "notifications/customer_ticket_to_work.txt"
        ).render({"ticket": ticket, "link": link})
        user = ticket.customer
        cls.objects.create(
            user=user,
            message=message,
            type_notify="ticket_to_work",
            emails=ticket._reply_to_emails,
            ticket=ticket,
        )

    @classmethod
    def create_notify_for_customer_when_ticket_to_done(cls, ticket: Ticket):
        link = ticket.get_external_url()
        message = loader.get_template("notifications/customer_ticket_done.txt").render(
            {
                "ticket": ticket,
                "link": link,
            }
        )
        user = ticket.customer
        notify = cls.objects.create(
            user=user,
            message=message,
            type_notify="ticket_done",
            emails=ticket._reply_to_emails,
            ticket=ticket,
            subject=f"Заявка №{ticket.sap_id or ticket.pk} выполнена",
        )
