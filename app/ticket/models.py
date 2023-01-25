from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model

from additionally.models import Dictionary

User = get_user_model()


def ticket_directory_path(instance, filename):
    return f"ticket_{instance.comment.ticket.pk}/{filename}"


class Ticket(models.Model):
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    sap_id = models.CharField("ID SAP заявки", max_length=30, null=True, blank=True)
    type_ticket = models.ForeignKey(
        Dictionary,
        verbose_name="Тип заявки",
        related_name="type_ticket",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    description = models.TextField(verbose_name="Описание")
    creator = models.ForeignKey(
        User,
        related_name="create_user",
        verbose_name="Автор",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    customer = models.ForeignKey(
        User,
        related_name="customer_user",
        verbose_name="Заказчик",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    planned_execution_date = models.DateField(
        "Плановая дата выезда/исполнения", null=True, blank=True
    )
    contractor = models.ForeignKey(
        User,
        related_name="contractor_user",
        verbose_name="Исполнитель",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    status = models.ForeignKey(
        Dictionary,
        verbose_name="Статус",
        help_text="В ожидании, в работе ...",
        related_name="status",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город")
    address = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Адрес"
    )

    shop_id = models.CharField(
        null=True, blank=True, max_length=50, verbose_name="ID магазина"
    )
    position = models.CharField(
        null=True, blank=True, max_length=50, verbose_name="Должность заказчика"
    )
    full_name = models.CharField(
        null=True, blank=True, max_length=50, verbose_name="Ф.И.О заказчика"
    )
    phone = models.CharField(
        null=True, blank=True, max_length=50, verbose_name="Телефон заказчика"
    )
    metadata = models.CharField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name="Другая информация",
        help_text="Дополнительная информация о заявке. Которая не вошла в другие поля",
    )

    id_email_message = models.CharField(
        verbose_name="ID письма в почте", null=True, blank=True, max_length=100
    )

    def __str__(self):
        return f"{self.pk} - {self.type_ticket}, {self.customer=}"

    def get_color_status(self):
        color = {
            "work": "blue",
            "search_contractor": "orange",
            "consideration": "teal",
            "revision": "yellow",
            "done": "green",
        }
        return color.get(self.status.code, "detail")

    def get_absolute_url(self):
        return reverse("ticket-update", kwargs={"pk": self.pk})


class Comment(models.Model):
    LEN_SHORT_TEXT = 10

    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    ticket = models.ForeignKey(
        Ticket, related_name="comments", on_delete=models.CASCADE
    )
    text = models.TextField("Текст комментария", null=True, blank=True)
    author = models.ForeignKey(
        User, related_name="comments", on_delete=models.SET_NULL, blank=True, null=True
    )
    id_email_message = models.CharField(
        verbose_name="ID письма в почте", null=True, blank=True, max_length=100
    )
    is_changed = models.BooleanField(default=False)

    def __str__(self) -> str:
        content = ""
        if self.text:
            content = self.get_short_text()
        if self.files:
            if content:
                content += " "
            content += f"[{self.files.count()} file(s)]"
        return f"[{self.ticket.pk}] {content}"

    def get_short_text(self) -> str:
        if self.text:
            if len(self.text) > self.LEN_SHORT_TEXT:
                return f"{self.text[:self.LEN_SHORT_TEXT]}... "
            return self.text
        return ""

    def get_absolute_url(self):
        return reverse("ticket-update", kwargs={"pk": self.ticket.pk})


class CommentFile(models.Model):
    comment = models.ForeignKey(Comment, related_name="files", on_delete=models.CASCADE)
    file = models.FileField(
        "Файл", upload_to=ticket_directory_path, null=True, blank=True
    )

    @property
    def file_name(self):
        return self.file.name.split("/")[-1]
