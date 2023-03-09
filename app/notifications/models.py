from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.conf import settings
from django.template import loader

from ticket.models import Ticket

User = get_user_model()


class Notification(models.Model):

    TYPE_NOTIFY = (
        ("new_ticket", "Новая заявка"),
        ("new_comment", "Новый комментарий"),
        ("set_contractor", "Установлен подрядчик"),
        ("ticket_to_work", "Заявка в работе"),
        ("ticket_done", "Заявка выполнена"),
        ("ticket_cancel", "Заявка отменена"),
        ("other", "Другое"),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    email = models.EmailField(blank=True, null=True)
    emails = models.TextField(blank=True, null=True)

    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    type_notify = models.CharField(
        "Тип оповещения", max_length=50, choices=TYPE_NOTIFY, default="other"
    )

    def get_emails(self):
        emails = set()
        if self.email:
            emails.add(self.email)
        if self.user and self.user.email:
            emails.add(self.user.email)
        if self.emails:
            emails.update(self.emails.split(","))
        return emails

    def __str__(self):
        return f"{self.user} - {self.message}"

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
        cls.objects.create(user=user, message=message)

    @classmethod
    def create_notify_for_customer_when_ticket_to_work(cls, ticket: Ticket):
        link = ticket.get_external_url()
        message = loader.get_template(
            "notifications/notify_customer_when_ticket_to_work.txt"
        ).render({"ticket": ticket, "link": link})
        user = ticket.customer
        cls.objects.create(user=user, message=message, type="ticket_to_work")
