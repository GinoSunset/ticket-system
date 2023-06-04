from django import forms

from ticket.widgets import CalendarInput
from additionally.models import DictionaryType, Dictionary
from .models import Manufacture, ManufactureNomenclature, Nomenclature


class ManufactureForm(forms.ModelForm):
    class Meta:
        model = Manufacture
        fields = [
            "status",
            "client",
            "date_shipment",
            "branding",
            "comment",
        ]
        widgets = {
            "date_shipment": CalendarInput(),
            "comment": forms.Textarea(attrs={"rows": 2}),
            "client": forms.Select(attrs={"class": "ui selection dropdown"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        type_status = DictionaryType.objects.get(code="status_manufactory")
        self.fields["status"].queryset = Dictionary.objects.filter(
            type_dict=type_status
        )
        self.fields["status"].initial = Dictionary.objects.get(
            type_dict=type_status, code="new_manufacture_task"
        )


class ManufactureNomenclatureForm(forms.ModelForm):
    nomenclature = forms.ModelChoiceField(
        queryset=Nomenclature.objects.all(),
        label="Номенклатура",
        widget=forms.Select(attrs={"class": "ui selection dropdown"}),
    )
    quantity = forms.IntegerField(min_value=1, label="Количество")

    class Meta:
        model = ManufactureNomenclature
        fields = (
            "nomenclature",
            "quantity",
        )


class NomenclatureForm(forms.ModelForm):
    class Meta:
        model = Nomenclature
        fields = (
            "name",
            "description",
        )
