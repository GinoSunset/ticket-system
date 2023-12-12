from django.db import models


class Component(models.Model):
    class Meta:
        verbose_name = "Компонент"
        verbose_name_plural = "Компоненты"

    component_type = models.ForeignKey(
        "ComponentType", verbose_name="Тип компонента", on_delete=models.CASCADE
    )
    serial_number = models.CharField(
        max_length=255, verbose_name="Серийный номер", null=True, blank=True
    )
    is_stock = models.BooleanField(default=False, verbose_name="В наличии")
    date_delivery = models.DateField(
        verbose_name="Дата получения", blank=True, null=True
    )
    is_reserve = models.BooleanField(default=False, verbose_name="Резерв")
    nomenclature = models.ForeignKey(
        "manufactures.Nomenclature",
        verbose_name="Номенклатура",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def get_status_color(self):
        if not self.is_stock and self.is_reserve and not self.date_delivery:
            return "red"
        if not self.is_stock and self.is_reserve and self.date_delivery:
            return "orange"
        if self.date_delivery:
            return "blue"
        if self.is_reserve:
            return "yellow"


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
    name = models.CharField(max_length=255, verbose_name="Название типа компонента")
    parent_component_type = models.ForeignKey(
        "ComponentType",
        verbose_name="Тип родительского подкомпонента",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="sub_components_type",
        help_text="Выберите тип компонента, в состав которого входит данный компонент",
    )
    is_internal = models.BooleanField(
        default=False,
        verbose_name="Для внутреннего использования",
        help_text="Если отмечено, то компонент  будет отображаться в списке компонентов только для инженеров",
    )

    def __str__(self) -> str:
        return f"{self.name} {f'[{self.sub_components_type.count()}]' if self.sub_components_type.all() else ''}"


class Delivery(models.Model):
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    date_delivery = models.DateField(verbose_name="Дата получения")
    comment = models.TextField(verbose_name="Комментарий", blank=True, null=True)
    components = models.ManyToManyField(
        "Component",
        verbose_name="Компоненты",
        related_name="deliveries",
        blank=True,
    )
