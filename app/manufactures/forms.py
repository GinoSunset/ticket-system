from django import forms

from ticket.widgets import CalendarInput
from additionally.models import DictionaryType, Dictionary
from .models import Manufacture, Nomenclature


class ManufactureForm(forms.ModelForm):
    class Meta:
        model = Manufacture
        fields = [
            "status",
            "client",
            "date_shipment",
            "branding",
            "comment",
            "nomenclatures",
        ]
        widgets = {
            "date_shipment": CalendarInput(),
            "comment": forms.Textarea(attrs={"rows": 2}),
            "client": forms.Select(attrs={"class": "ui selection dropdown"}),
            "nomenclatures": forms.SelectMultiple(
                attrs={"class": "ui fluid search dropdown"}
            ),
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

    # when save form add count as sum nomenclatures tx_count and rx_count
    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()
            self.save_m2m()
            instance.count = sum(
                [
                    nomenclature.tx_count + nomenclature.rx_count
                    for nomenclature in instance.nomenclatures.all()
                ]
            )
            instance.save()
        return instance


class NomenclatureForm(forms.ModelForm):
    class Meta:
        model = Nomenclature
        fields = (
            "frame_type",
            "body",
            "tx_count",
            "rx_count",
            "mdg",
            "md",
            "wifi",
            "bd_type",
            "bd_count",
            "illumination",
            "comment",
        )
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 2}),
            "frame_type": forms.RadioSelect(),
            "body": forms.RadioSelect(),
            "bd_type": forms.RadioSelect(),
        }
