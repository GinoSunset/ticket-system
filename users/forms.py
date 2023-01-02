from django.forms import ModelForm

from .models import Customer


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
