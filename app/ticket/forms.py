from django import forms
from additionally.models import Dictionary, DictionaryType
from .models import Ticket, Comment
from .widgets import CalendarInput, ContractorSelect
from users.models import Contractor


class TicketsForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
            "sap_id",
            "type_ticket",
            "description",
            "customer",
            "contractor",
            "status",
            "city",
            "address",
            "planned_execution_date",
            "shop_id",
            "position",
            "full_name",
            "phone",
            "metadata",
        ]
        widgets = {
            "planned_execution_date": CalendarInput(),
            "contractor": ContractorSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        type_ticket = DictionaryType.objects.get(code="type_ticket")
        type_status = DictionaryType.objects.get(code="status_ticket")
        self.fields["type_ticket"].queryset = Dictionary.objects.filter(
            type_dict=type_ticket
        )
        self.fields["type_ticket"].initial = kwargs.get("initial").get("type_ticket")

        self.fields["status"].queryset = Dictionary.objects.filter(
            type_dict=type_status
        )

        self.fields["contractor"].queryset = Contractor.objects.all()
        if "customer_qs" in kwargs["initial"]:
            self.fields["customer"].queryset = kwargs["initial"].get("customer_qs")
            self.fields["customer"].initial = kwargs["initial"].get("customer")


class TicketsFormOperator(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
            "sap_id",
            "type_ticket",
            "description",
            "city",
            "address",
            "status",
            "shop_id",
            "position",
            "full_name",
            "phone",
            "metadata",
        ]
        widgets = {
            "status": forms.TextInput(attrs={"type": "hidden"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        type_ticket = DictionaryType.objects.get(code="type_ticket")
        self.fields["type_ticket"].queryset = Dictionary.objects.filter(
            type_dict=type_ticket
        )


class CommentForm(forms.ModelForm):
    files = forms.FileField(
        required=False,
        help_text="Файлы",
        label="Прикрепить файлы",
        widget=forms.ClearableFileInput(attrs={"multiple": True}),
    )

    class Meta:
        model = Comment
        fields = ["text"]
