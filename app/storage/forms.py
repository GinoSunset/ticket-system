from django import forms
from django.forms import ModelForm, TextInput, inlineformset_factory
from .models import ComponentType, Alias


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


AliasFormSet = inlineformset_factory(ComponentType, Alias, form=AliasForm, extra=1)
