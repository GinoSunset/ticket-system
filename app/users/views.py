from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from .forms import CustomerForm, ContractorForm
from .models import Customer, Contractor


class CreateCustomerView(LoginRequiredMixin, CreateView):
    form_class = CustomerForm
    template_name = "users/user_form.html"
    success_url = "/"

    def form_valid(self, form):
        self.object: Customer = form.save()
        self.object.profile.linked_operators.add(self.request.user.get_role_user())
        return super().form_valid(form)


class CreateContractorView(LoginRequiredMixin, CreateView):
    form_class = ContractorForm
    template_name = "users/user_form.html"
    success_url = "/"

    def form_valid(self, form):
        self.object: Contractor = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["name_page"] = "Создать исполнителя"
        return context


class ListCustomerView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = "users/customer_list.html"

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Customer.objects.all()
        return Customer.objects.filter(
            profile__linked_operators=self.request.user.get_role_user()
        )


class ListContractorView(LoginRequiredMixin, ListView):
    model = Contractor
    template_name = "users/contractor_list.html"


class UpdateCustomer(LoginRequiredMixin, UpdateView):
    form_class = CustomerForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("list-customers")

    def get_object(self, queryset=None):
        user = self.request.user.get_role_user()
        if user.is_superuser:
            return Customer.objects.get(pk=self.kwargs["pk"])
        if user.is_operator:
            try:
                return Customer.objects.get(
                    pk=self.kwargs["pk"], profile__linked_operators=user
                )
            except Customer.DoesNotExist:
                pass
        raise Http404()

    def form_valid(self, form):
        self.object: Customer = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["name_page"] = "Изменить данные клиента"
        context["name_btn"] = "Изменить"
        return context


class UpdateContractorView(LoginRequiredMixin, UpdateView):
    form_class = ContractorForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("list-contractors")
    model = Contractor

    def form_valid(self, form):
        self.object: Customer = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["name_page"] = "Изменить данные клиента"
        context["name_btn"] = "Изменить"
        return context
