from django import forms

from ticket.widgets import CalendarInput

from .models import Report


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["start_date", "end_date"]

        widgets = {
            "start_date": CalendarInput(),
            "end_date": CalendarInput(),
        }
