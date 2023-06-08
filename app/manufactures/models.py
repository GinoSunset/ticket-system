from django.db import models

from additionally.models import Dictionary
from users.models import Operator


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
        blank=True,
    )
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    operator = models.ForeignKey(
        Operator,
        verbose_name="Оператор",
        on_delete=models.PROTECT,
    )

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
    nomenclatures = models.ManyToManyField(
        "Nomenclature",
        verbose_name="Номенклатуры",
        related_name="manufactures",
        blank=True,
        through="ManufactureNomenclature",
    )

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
        ordering = ["-date_create"]

    class FrameType(models.TextChoices):
        PRODUCT = "AM", "AM"
        SERVICE = "RF", "РЧ"

    class Body(models.TextChoices):
        PLEX = "PL", "Плекс"
        PROFILE = "PR", "Профиль"
        S = "S", "S"

    class BDType(models.TextChoices):
        INNER = "IN", "Внутренний"
        OUTER = "OU", "Внешний"

    frame_type = models.CharField(
        verbose_name="Тип",
        choices=FrameType.choices,
        default=FrameType.PRODUCT,
        max_length=2,
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
    wifi = models.BooleanField(verbose_name="Wifi", default=False)

    bd_type = models.CharField(
        verbose_name="Тип БД",
        choices=BDType.choices,
        default=BDType.INNER,
        max_length=2,
    )
    bd_count = models.IntegerField(verbose_name="Количество БД", default=1)
    illumination = models.BooleanField(verbose_name="Подсветка", default=False)

    comment = models.TextField(verbose_name="Комментарий", blank=True, null=True)
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

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
        return f"[{self.pk}]{self.frame_type} {self.body} RX:{self.tx_count} TX:{self.rx_count} {options} {self.bd_type} {self.bd_count} {illumination}"


class ManufactureNomenclature(models.Model):
    manufacture = models.ForeignKey(
        Manufacture,
        verbose_name="Заявка на производство",
        on_delete=models.PROTECT,
        related_name="manufacture_nomenclatures",
    )
    nomenclature = models.ForeignKey(
        Nomenclature,
        verbose_name="Номенклатура",
        on_delete=models.PROTECT,
        related_name="manufacture_nomenclatures",
    )
    quantity = models.IntegerField(verbose_name="Количество", default=1)
    comment = models.TextField(verbose_name="Комментарий", blank=True, null=True)
