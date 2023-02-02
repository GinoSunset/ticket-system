from django import forms

from .models import Customer, Contractor, ContractorProfile


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "email",
            "username",
            "phone",
            "first_name",
            "last_name",
        ]


class ContractorForm(forms.ModelForm):
    city = forms.CharField(label="Город", max_length=50, required=False)
    region = forms.CharField(label="Область", max_length=100, required=False)
    note = forms.CharField(label="Примечание", required=False)

    class Meta:
        model = Contractor
        fields = [
            "email",
            "username",
            "phone",
            "first_name",
            "last_name",
        ]
