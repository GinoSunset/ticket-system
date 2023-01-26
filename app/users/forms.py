from django.forms import ModelForm

from .models import Customer, Contractor


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = [
            "email",
            "username",
            "phone",
            "first_name",
            "last_name",
        ]


class ContractorForm(ModelForm):
    class Meta:
        model = Contractor
        fields = [
            "email",
            "username",
            "phone",
            "first_name",
            "last_name",
        ]
