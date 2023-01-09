from django.forms import ModelForm, TextInput
from additionally.models import Dictionary, DictionaryType
from .models import Ticket, Comment
from users.models import CustomerProfile, Operator, Contractor, Customer


class TicketsForm(ModelForm):
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
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        type_ticket = DictionaryType.objects.get(code="type_ticket")
        type_status = DictionaryType.objects.get(code="status_ticket")
        self.fields["type_ticket"].queryset = Dictionary.objects.filter(
            type_dict=type_ticket
        )
        self.fields["status"].queryset = Dictionary.objects.filter(
            type_dict=type_status
        )
        self.fields["contractor"].queryset = Contractor.objects.all()
        if kwargs["initial"].get("customer_qs"):
            self.fields["customer"].queryset = kwargs["initial"].get("customer_qs")


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["text", "file"]


class TicketsFormOperator(ModelForm):
    class Meta:
        model = Ticket
        fields = ["sap_id", "type_ticket", "description", "city", "address", "status"]
        widgets = {
            "status": TextInput(attrs={"type": "hidden"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        type_ticket = DictionaryType.objects.get(code="type_ticket")
        self.fields["type_ticket"].queryset = Dictionary.objects.filter(
            type_dict=type_ticket
        )
