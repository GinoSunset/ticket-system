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
    count = models.IntegerField(verbose_name="Количество", default=1)
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
        ordering = ["-name"]

    name = models.CharField(verbose_name="Наименование", max_length=100)
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


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
