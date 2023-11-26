from django.db import models

from additionally.models import Dictionary
from users.models import Operator


def get_default_new_manufacture_status():
    status, _ = Dictionary.objects.get_or_create(
        code="new_manufacture_task", type_dict__code="status_manufactory"
    )
    return status


#  Option
class Option(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class FrameTypeOption(Option):
    pass

    @classmethod
    def get_default(cls):
        frame_type, _ = cls.objects.get_or_create(name="АМ")
        return frame_type.pk


class Manufacture(models.Model):
    class Meta:
        verbose_name = "Заявка на производство"
        verbose_name_plural = "Заявки на производство"
        ordering = ["-date_create"]

    status = models.ForeignKey(
        Dictionary,
        verbose_name="Статус",
        help_text="В ожидании, в работе ...",
        related_name="manufactures_status",
        on_delete=models.SET_NULL,
        null=True,
        default=get_default_new_manufacture_status,
    )
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    operator = models.ForeignKey(
        Operator,
        verbose_name="Оператор",
        on_delete=models.PROTECT,
    )
    count = models.IntegerField(verbose_name="Количество", default=0)
    client = models.ForeignKey(
        "Client",
        verbose_name="Клиент",
        on_delete=models.PROTECT,
        related_name="manufactures",
    )
    date_shipment = models.DateField(
        verbose_name="Дата отгрузки", blank=True, null=True
    )
    branding = models.BooleanField(verbose_name="Брендирование", default=False)
    comment = models.TextField(verbose_name="Комментарий", blank=True, null=True)

    @property
    def progress_str_as_list_nomenclatures(self) -> str:
        """return list with count nomenclatures in work and in status ready"""
        list_progress = [
            self.nomenclatures.filter(status=Nomenclature.Status.IN_PROGRESS).count(),
            self.nomenclatures.filter(status=Nomenclature.Status.READY).count(),
        ]
        return ",".join([str(i) for i in list_progress])

    def get_color_status(self):
        color = {
            "in_progress": "blue",
            "ready": "green",
            "new_manufacture_task": "violet",
        }
        return color.get(self.status.code, "detail")


class Client(models.Model):
    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ["-name"]

    name = models.CharField(verbose_name="Имя", max_length=100)
    comment = models.TextField(verbose_name="Комментарий", blank=True, null=True)
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class Nomenclature(models.Model):
    class Meta:
        verbose_name = "Номенклатура"
        verbose_name_plural = "Номенклатуры"
        ordering = ["date_create"]

    class Body(models.TextChoices):
        PLEX = "PL", "Плекс"
        PROFILE = "PR", "Профиль"
        S_WHITE = "SW", "S Белый"
        S_GREY = "SG", "S Серый"
        S_BLACK = "SB", "S Черный"

    class BDType(models.TextChoices):
        OUTER = "OU", "Внешний"
        INNER = "IN", "Внутренний"

    class Color(models.TextChoices):
        WHITE = "WH", "Белый"
        GREY = "GR", "Серый"
        BLACK = "BL", "Черный"

    class Status(models.IntegerChoices):
        NEW = 1, "Новый"
        IN_PROGRESS = 2, "В работе"
        READY = 3, "Готово"

    status = models.IntegerField(
        verbose_name="Статус",
        choices=Status.choices,
        default=Status.NEW,
    )

    frame_type = models.ForeignKey(
        FrameTypeOption,
        verbose_name="Тип",
        on_delete=models.PROTECT,
        default=FrameTypeOption.get_default,
    )

    body = models.CharField(
        verbose_name="Корпус",
        choices=Body.choices,
        default=Body.PLEX,
        max_length=2,
    )

    tx_count = models.IntegerField(verbose_name="Количество TX", default=1)
    rx_count = models.IntegerField(verbose_name="Количество RX", default=1)

    mdg = models.BooleanField(verbose_name="MDG", default=False)
    md = models.BooleanField(verbose_name="MD", default=False)
    wifi = models.BooleanField(verbose_name="Wi-Fi", default=False)

    bp_type = models.CharField(
        verbose_name="Тип БП",
        choices=BDType.choices,
        default=BDType.OUTER,
        max_length=2,
    )
    bp_count = models.IntegerField(verbose_name="Количество БП", default=1)

    amperage_6 = models.BooleanField(
        verbose_name="6 А", default=False, help_text="Amperage for RF"
    )
    amperage_3_2 = models.BooleanField(
        verbose_name="3.2 А", default=False, help_text="Amperage for RF"
    )
    amperage_1 = models.BooleanField(
        verbose_name="1 А", default=False, help_text="Amperage for AM"
    )
    amperage_2 = models.BooleanField(
        verbose_name="2 А", default=False, help_text="Amperage for AM"
    )

    illumination = models.BooleanField(verbose_name="Подсветка", default=True)

    comment = models.TextField(verbose_name="Комментарий", blank=True, null=True)
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    manufacture = models.ForeignKey(
        Manufacture,
        verbose_name="Заявка на производство",
        on_delete=models.CASCADE,
        related_name="nomenclatures",
        null=True,
        blank=True,
    )

    def __str__(self):
        options = []
        if self.mdg:
            options.append("MGD")
        if self.md:
            options.append("MD")
        if self.wifi:
            options.append("WIFI")
        options = "/".join(options)
        illumination = "💡" if self.illumination else ""
        return f"[{self.pk}]{self.frame_type} {self.body} RX:{self.tx_count} TX:{self.rx_count} {options} {self.bp_type} {self.bp_count} {illumination}"
