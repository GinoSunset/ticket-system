from django.urls import reverse
from django.views.generic.edit import CreateView
from .forms import CustomerForm
from .models import Customer


class CreateCustomerView(CreateView):
    form_class = CustomerForm
    template_name = "users/customer_form.html"
    success_url = "/"

    def form_valid(self, form):
        self.object: Customer = form.save()
        self.object.profile.linked_operators.add(self.request.user.get_role_user())
        return super().form_valid(form)
