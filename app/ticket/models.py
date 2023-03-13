import re

from additionally.models import Dictionary
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.db import models
from django.urls import reverse
from django.utils import timezone
from reports.utils import create_act_for_ticket
from users.models import Operator

User = get_user_model()


def ticket_directory_path(instance, filename):
    return f"ticket_{instance.comment.ticket.pk}/{filename}"


class Ticket(models.Model):
    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ["-date_create"]

    default_type_code = "hardware_setup"

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

    responsible = models.ForeignKey(
        Operator,
        verbose_name="Ответственный",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    completion_date = models.DateTimeField(
        "Дата завершения", null=True, blank=True, help_text="Дата завершения заявки"
    )

    date_to_work = models.DateTimeField(
        "Дата взятия в работу", null=True, blank=True, help_text="Дата взятия в работу"
    )

    _reply_to_emails = models.CharField(
        "Адреса для ответов", max_length=1000, null=True, blank=True
    )

    @property
    def reply_to_emails(self):
        if self._reply_to_emails:
            return self._reply_to_emails.split(",")
        return []

    def __str__(self):
        return f"{self.pk} - {self.type_ticket}, {self.customer=}"

    def get_color_status(self):
        color = {
            "work": "blue",
            "search_contractor": "orange",
            "consideration": "teal",
            "revision": "yellow",
            "done": "green",
            "new": "violet",
            "testing": "pink",
        }
        return color.get(self.status.code, "detail")

    def get_absolute_url(self):
        return reverse("ticket-update", kwargs={"pk": self.pk})

    def get_external_url(self):
        return f"{settings.PROTOCOL}://{Site.objects.get_current()}{self.get_absolute_url()}"

    def get_comments_for_report(self):
        comments = self.comments.filter(is_system_message=False, text__isnull=False)
        comments = comments.exclude(is_for_report=False)
        comments = comments.exclude(text__in=Comment.NO_REPORT_TEXTS)
        return comments

    def get_colored_status_if_dup_shop(self):
        if self.status and self.status.code == "new":
            if self.is_dup_shop():
                return "violet colored"
        return

    def is_dup_shop(self):
        return Ticket.objects.filter(shop_id=self.shop_id).count() >= 2

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.pk:
            if self.status == Dictionary.objects.get(code="done"):
                self.completion_date = timezone.now()
            if self.status == Dictionary.objects.get(code="work"):
                if not self.date_to_work:
                    self.date_to_work = timezone.now()
                    self.save()
                if not hasattr(self, "act"):
                    self.act = create_act_for_ticket(ticket=self)
                if not self.act.file_doc_act:
                    self.act.create_act()
        return super().save(force_insert, force_update, using, update_fields)


class Comment(models.Model):
    NO_REPORT_TEXTS = ["Вложение из письма", ""]

    TEMPLATE_DICT = {
        "status": "{field} изменен c '{prev_value}' на '{value}'\n",
        "contractor": "{value} назначен(а) исполнителем\n",
        "planned_execution_date": "Планируемая дата выезда назначена на: {value}\n",
        "responsible": "{value} назначен(а) ответственным\n",
    }

    class Meta:
        ordering = ("-date_create",)
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

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
    is_system_message = models.BooleanField(default=False)
    is_for_report = models.BooleanField(default=False)

    def __str__(self) -> str:
        content = ""
        if self.text:
            content = self.get_short_text()
        if self.files:
            if content:
                content += " "
            content += f"[{self.files.count()} file(s)]"
        if self.images:
            if content:
                content += " "
            content += f"[{self.images.count()} image(s)]"
        return f"[{self.ticket.pk}] {content}"

    def comment_for_report(self):
        header = f"[{self.author}-{self.date_create.strftime('%d-%m-%Y')}]"
        return f"{header}\n{self.clean_text_from_html(self.text)}"

    @staticmethod
    def clean_text_from_html(text: str) -> str:
        if "<div>" not in text:
            return text
        html_tag_pattern = re.compile(r"<[^>]+>")
        text_without_html = re.sub(html_tag_pattern, "", text)
        return f"<! удалены html теги !>{text_without_html}"

    def get_short_text(self) -> str:
        if self.text:
            if len(self.text) > self.LEN_SHORT_TEXT:
                return f"{self.text[:self.LEN_SHORT_TEXT]}... "
            return self.text
        return ""

    def get_absolute_url(self):
        return reverse("ticket-update", kwargs={"pk": self.ticket.pk})

    @classmethod
    def create_update_system_comment(cls, text, ticket, user):
        Comment.objects.create(
            ticket=ticket,
            author=user,
            text=text,
            is_system_message=True,
        )

    @classmethod
    def get_text_system_comment(cls, changed_data, initial_data, named_field, ticket):

        text = ""
        for field in changed_data:
            value = getattr(ticket, field)
            value = str(value) if value else "Пусто"
            message = cls.TEMPLATE_DICT.get(
                field, "Поле {field} изменено c '{prev_value}' на '{value}'\n"
            )
            text += message.format(
                field=(named_field[field]),
                prev_value=initial_data.get(field, "Пусто") or "Не указано",
                value=value,
            )

        return text


class CommentFile(models.Model):
    class Meta:
        verbose_name = "Файл комментария"
        verbose_name_plural = "Файлы комментариев"

    comment = models.ForeignKey(Comment, related_name="files", on_delete=models.CASCADE)
    file = models.FileField(
        "Файл", upload_to=ticket_directory_path, null=True, blank=True
    )

    @property
    def file_name(self):
        return self.file.name.split("/")[-1]


class CommentImage(models.Model):
    class Meta:
        verbose_name = "Изображение комментария"
        verbose_name_plural = "Изображения комментариев"

    comment = models.ForeignKey(
        Comment, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(
        "Изображение", upload_to=ticket_directory_path, null=True, blank=True
    )

    @property
    def image_name(self):
        return self.image.name.split("/")[-1]
