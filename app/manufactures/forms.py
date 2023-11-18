from django import forms

from ticket.widgets import CalendarInput, FomanticRadioSelect
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
        ]
        widgets = {
            "date_shipment": CalendarInput(),
            "comment": forms.Textarea(attrs={"rows": 1, "placeholder": "Комментарий"}),
            "client": forms.Select(attrs={"class": "ui selection dropdown"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        type_status = DictionaryType.objects.get(code="status_manufactory")
        self.fields["status"].queryset = Dictionary.objects.filter(
            type_dict=type_status
        )


class NomenclatureForm(forms.ModelForm):
    id = forms.IntegerField(
        widget=forms.HiddenInput(), required=False, label="id_nomenclature"
    )

    class Meta:
        model = Nomenclature
        fields = (
            "id",
            "frame_type",
            "body",
            "tx_count",
            "rx_count",
            "mdg",
            "md",
            "wifi",
            "bp_type",
            "bp_count",
            "illumination",
            "comment",
            "status",
            "amperage_6",
            "amperage_3_2",
            "amperage_1",
            "amperage_2",
        )
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 2, "placeholder": "Комментарий"}),
            "frame_type": forms.Select(
                attrs={"class": "ui selection dropdown frame_type"}
            ),
            "body": forms.Select(attrs={"class": "ui selection dropdown"}),
            "bp_type": forms.Select(attrs={"class": "ui selection dropdown"}),
            "status": forms.Select(attrs={"class": "ui selection dropdown"}),
            "amperage_6": forms.CheckboxInput(attrs={"class": "ui checkbox"}),
            "amperage_3_2": forms.CheckboxInput(attrs={"class": "ui checkbox"}),
            "amperage_1": forms.CheckboxInput(attrs={"class": "ui checkbox"}),
            "amperage_2": forms.CheckboxInput(attrs={"class": "ui checkbox"}),
        }


class ManufactureChangeStatusForm(forms.ModelForm):
    status = forms.ModelChoiceField(
        queryset=Dictionary.objects.filter(type_dict__code="status_manufactory"),
    )

    class Meta:
        model = Manufacture
        fields = ("status",)
        widgets = {
            "status": forms.Select(attrs={"class": "ui selection dropdown"}),
        }
