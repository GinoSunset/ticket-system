from django import forms

from ticket.widgets import CalendarInput
from .models import Manufacture


class ManufactureForm(forms.ModelForm):
    class Meta:
        model = Manufacture
        fields = ["status", "client", "date_shipment", "branding", "comment"]
        widgets = {
            "date_shipment": CalendarInput(),
        }
