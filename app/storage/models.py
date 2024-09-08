import datetime
import uuid
from django.db import models
from django.db.models import Case, When, Value, BooleanField, Count


class TagComponent(models.Model):
    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    name = models.CharField(max_length=255, verbose_name="Тег", unique=True)

    def __str__(self) -> str:
        return self.name


class ComponentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_archive=False)


class ComponentPhantomManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                phantom=Case(
                    When(
                        is_archive=False,
                        is_stock=False,
                        date_delivery=None,
                        then=Value(True),
                    ),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )
        )


class Component(models.Model):
    class Meta:
        verbose_name = "Компонент"
        verbose_name_plural = "Компоненты"

    component_type = models.ForeignKey(
        "ComponentType",
        verbose_name="Тип компонента",
        on_delete=models.CASCADE,
    )
    is_archive = models.BooleanField(default=False, verbose_name="В архиве")

    serial_number = models.CharField(
        max_length=255, verbose_name="Серийный номер", null=True, blank=True
    )
    is_stock = models.BooleanField(default=False, verbose_name="В наличии")
    date_delivery = models.DateField(
        verbose_name="Дата получения", blank=True, null=True
    )
    delivery = models.ForeignKey(
        "Delivery", verbose_name="Доставка", on_delete=models.CASCADE, null=True
    )
    is_reserve = models.BooleanField(default=False, verbose_name="Резерв")
    nomenclature = models.ForeignKey(
        "manufactures.Nomenclature",
        verbose_name="Номенклатура",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    active_components = ComponentManager()
    phantom_components = ComponentPhantomManager()
    objects = models.Manager()

    @classmethod
    def generate_serial_number(cls, component_type):
        def get_prefix():
            if " " in component_type.name:
                return "".join([word[0] for word in component_type.name.split()])
            return component_type.name[:2]

        while True:
            serial_number = f"{get_prefix()}-{uuid.uuid4().hex[:8]}".upper()
            if not Component.objects.filter(serial_number=serial_number).exists():
                return serial_number

    def get_status_color(self):
        if not self.is_stock and self.is_reserve and not self.date_delivery:
            return "red"
        if not self.is_stock and self.is_reserve and self.date_delivery:
            return "violet"
        if self.is_stock and self.is_reserve:
            return "purple"
        if self.date_delivery:
            return "blue"

    @property
    def is_phantom(self) -> bool:
        return all(
            [
                self.is_archive is False,
                self.is_stock is False,
                self.delivery is None,
                self.date_delivery is None,
            ]
        )

    @property
    def tags(self):
        return self.component_type.tags

    def __str__(self) -> str:
        sn = f" {self.serial_number}" or ""
        return f"[{self.pk}]{self.component_type.name}{sn}"


class Alias(models.Model):
    class Meta:
        verbose_name = "Алиас"
        verbose_name_plural = "Алиасы"
        unique_together = ("name", "component_type")

    name = models.CharField(max_length=255, verbose_name="Алиас")
    component_type = models.ForeignKey(
        "ComponentType", verbose_name="Тип компонента", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.name}->({self.component_type})"


class ComponentType(models.Model):
    class Meta:
        verbose_name = "Тип компонента"
        verbose_name_plural = "Типы компонентов"

    name = models.CharField(
        max_length=255, verbose_name="Название типа компонента", unique=True
    )
    sub_components_type = models.ManyToManyField(
        "ComponentType",
        verbose_name="Тип подкомпонента",
        related_name="parent_component_type",
        through="SubComponentTypeRelation",
    )
    is_internal = models.BooleanField(
        default=False,
        verbose_name="Для внутреннего использования",
        help_text="Если отмечено, то компонент будет отображаться в списке компонентов только для инженеров",
    )

    tags = models.ManyToManyField(TagComponent)

    def __str__(self) -> str:
        return f"{self.name}"


class SubComponentTypeRelation(models.Model):
    class Meta:
        verbose_name = "Связь типов компонентов"
        verbose_name_plural = "Связь типов компонентов"

    parent_component_type = models.ForeignKey(
        "ComponentType",
        verbose_name="Родительский компонент",
        related_name="sub_components",
        on_delete=models.PROTECT,
    )
    sub_component_type = models.ForeignKey(
        "ComponentType",
        verbose_name="Тип подкомпонента",
        related_name="parent_components",
        on_delete=models.CASCADE,
    )
    count_sub_components = models.PositiveIntegerField(
        verbose_name="Количество", default=1
    )

    def __str__(self) -> str:
        return f"{self.parent_component_type.name} -> {self.sub_component_type} [{self.count_sub_components}]"


class Delivery(models.Model):
    class Meta:
        verbose_name = "Доставка"
        verbose_name_plural = "Доставки"
        ordering = ["-date_delivery"]

    class Status(models.IntegerChoices):
        DRAFT = 5, "Черновик"
        NEW = 10, "Создана"
        DONE = 30, "Завершена"
        CANCELED = 50, "Отменена"

    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    date_delivery = models.DateField(verbose_name="Дата получения")
    comment = models.TextField(verbose_name="Комментарий", blank=True, null=True)
    status = models.IntegerField(
        verbose_name="Статус",
        choices=Status.choices,
        default=Status.NEW,
    )

    def __str__(self) -> str:
        return f"#{self.pk} [{self.date_delivery}] {self.component_set.count()} - Компонент(а)ов"

    def get_color(self):
        match self.status:
            case self.Status.NEW if self.is_outdate:
                return "red"
            case self.Status.NEW if self.date_delivery == datetime.date.today():
                return "yellow"
            case self.Status.NEW:
                return "green"
            case self.Status.DONE:
                return "black"
            case _:
                return ""

    @property
    def is_outdate(self):
        return self.date_delivery < datetime.date.today()

    def get_component_total_aggregate(self):
        return (
            self.component_set.all()
            .values("component_type__name")
            .annotate(total=Count("id"))
        )


class Invoice(models.Model):
    class Meta:
        verbose_name = "Счет на доставку"
        verbose_name_plural = "Счета на доставку"
    class Status(models.IntegerChoices):
        NEW = 5, "Новый"
        WORK = 10, "В работе"
        DONE = 20, "Обработан"
        ERROR = 100, "Ошибка"

    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    file_invoice = models.FileField(
        upload_to="secret/invoice/%Y/%m/", verbose_name="Счет"
    )
    delivery = models.OneToOneField(
        "Delivery", verbose_name="Доставка", on_delete=models.SET_NULL, null=True
    )
    alias = models.ManyToManyField(Alias)
    status = models.IntegerField(
        verbose_name="Статус",
        choices=Status.choices,
        default=Status.NEW,
    )

    def to_work(self):
        if self.status is not self.Status.WORK:
            # go to process
            self.status = self.Status.WORK
            self.save()
            # loggings

    def __str__(self) -> str:
        return f"[{self.delivery.pk}] - file: {self.file_invoice.name}"