from django import forms
from django.forms import ModelForm
from .models import ComponentType, Alias, Component


class AliasForm(ModelForm):
    class Meta:
        model = Alias
        fields = ["name"]


class ComponentTypeForm(ModelForm):
    class Meta:
        model = ComponentType
        fields = ["name", "is_internal", "parent_component_type"]

        widgets = {
            "is_internal": forms.CheckboxInput(attrs={"class": "ui checkbox"}),
        }


class ComponentForm(ModelForm):
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
            "is_stock": forms.CheckboxInput(attrs={"class": "ui checkbox"}),
            "is_reserve": forms.CheckboxInput(attrs={"class": "ui checkbox"}),
            "date_delivery": forms.DateInput(attrs={"type": "date"}),
            "component_type": forms.Select(attrs={"class": "ui dropdown search "}),
            "nomenclature": forms.Select(
                attrs={"class": "ui dropdown search clearable"}
            ),
        }
