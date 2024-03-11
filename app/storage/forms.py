from django import forms
from django.forms import ModelForm, Form
from django.forms.formsets import formset_factory
from django.core.exceptions import ValidationError
from ticket.widgets import CalendarInput
from .models import ComponentType, Alias, Component, SubComponentTypeRelation, Delivery

from ticsys.widgets import Dropdown


class AliasForm(ModelForm):
    class Meta:
        model = Alias
        fields = ["name"]


class ComponentTypeForm(ModelForm):
    class Meta:
        model = ComponentType
        fields = ["name", "is_internal"]

        widgets = {
            "is_internal": forms.CheckboxInput(attrs={"class": "ui checkbox"}),
        }


class ComponentForm(ModelForm):
    count = forms.IntegerField(
        required=True,
        label="Количество компонентов",
        initial=1,
        min_value=1,
        help_text="Количество компонентов, которые необходимо добавить",
    )
    generate_serial_number = forms.BooleanField(
        required=False,
        label="Сгенерировать серийный номер",
        initial=False,
        help_text="нужно ли генерировать серийный номер компонентов у которых их нет",
    )

    class Meta:
        model = Component
        fields = [
            "component_type",
            "serial_number",
            "is_stock",
            "date_delivery",
            "is_reserve",
            "nomenclature",
        ]

        widgets = {
            "is_stock": forms.CheckboxInput(
                attrs={"class": "ui checkbox", "checked": True},
            ),
            "is_reserve": forms.CheckboxInput(attrs={"class": "ui checkbox"}),
            "date_delivery": forms.DateInput(attrs={"type": "date"}),
            "component_type": forms.Select(attrs={"class": "ui dropdown search "}),
            "nomenclature": forms.Select(
                attrs={"class": "ui dropdown search clearable"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_stock = cleaned_data.get("is_stock")
        is_reserve = cleaned_data.get("is_reserve")
        date_delivery = cleaned_data.get("date_delivery")

        if not is_stock and not is_reserve and not date_delivery:
            raise ValidationError(
                "Необходимо указать статус компонента (в наличии или в резерве) или указать дату поставки"
            )


class ParentTypeForm(ModelForm):
    class Meta:
        model = SubComponentTypeRelation
        fields = ["parent_component_type", "count_sub_components"]

        widgets = {
            "parent_component_type": forms.Select(
                attrs={
                    "class": "ui dropdown search",
                    "placeholder": "Выберите тип",
                    "required": True,
                }
            ),
        }


ParentFormSet = formset_factory(ParentTypeForm, min_num=1, validate_min=True, extra=0)


class DeliveryForm(ModelForm):
    class Meta:
        model = Delivery
        fields = ["date_delivery", "comment"]

        widgets = {
            "date_delivery": CalendarInput(),
        }


class TypeComponentCountForm(Form):
    component_type = forms.ModelChoiceField(
        queryset=ComponentType.objects.all(),
        label="Тип компонента",
        required=True,
        widget=forms.Select(
            attrs={
                "class": "ui dropdown search",
                "placeholder": "Выберите тип",
                "required": True,
            }
        ),
    )
    count = forms.IntegerField(min_value=1, initial=1, label="Количество в доставке")


TypeComponentCountFormSet = formset_factory(
    TypeComponentCountForm, min_num=1, validate_min=True, extra=0
)
