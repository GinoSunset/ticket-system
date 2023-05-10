from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from ticket.mixin import AccessOperatorMixin
from .forms import CustomerForm, ContractorForm
from .models import Customer, Contractor, ContractorProfile, User


class CreateCustomerView(LoginRequiredMixin, CreateView):
    form_class = CustomerForm
    template_name = "users/user_form.html"
    success_url = "/"

    def form_valid(self, form):
        self.object: Customer = form.save()
        self.object.profile.linked_operators.add(self.request.user.get_role_user())
        self.object.profile.company = form.cleaned_data["company"]
        return super().form_valid(form)


class CreateContractorView(LoginRequiredMixin, CreateView):
    form_class = ContractorForm
    template_name = "users/user_form.html"
    success_url = "/"

    def form_valid(self, form):
        self.object: Contractor = form.save()
        self.object.profile_contractor.city = form.cleaned_data["city"]
        self.object.profile_contractor.region = form.cleaned_data["region"]
        self.object.profile_contractor.company = form.cleaned_data["company"]
        self.object.profile_contractor.note = form.cleaned_data["note"]
        self.object.profile_contractor.save()
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


class ListContractorJsonView(LoginRequiredMixin, AccessOperatorMixin, ListView):
    model = Contractor

    def render_to_response(self, context, **response_kwargs):
        """first_name, last_name, company, city, region, note"""
        return JsonResponse(
            {
                "data": [
                    [
                        contractor.id,
                        contractor.first_name,
                        contractor.last_name,
                        contractor.profile_contractor.company,
                        contractor.profile_contractor.city,
                        contractor.profile_contractor.region,
                        contractor.profile_contractor.note,
                    ]
                    for contractor in context["object_list"]
                ]
            }
        )


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
        self.object.profile.company = form.cleaned_data["company"]
        self.object.profile.save()
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        initial["company"] = self.object.profile.company
        return initial

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
        if not hasattr(self.object, "profile_contractor"):
            self.object.profile_contractor = ContractorProfile.objects.create(
                user=self.object
            )
        self.object.profile_contractor.city = form.cleaned_data["city"]
        self.object.profile_contractor.region = form.cleaned_data["region"]
        self.object.profile_contractor.note = form.cleaned_data["note"]
        self.object.profile_contractor.company = form.cleaned_data["company"]
        self.object.profile_contractor.save()
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        if hasattr(self.object, "profile_contractor"):
            initial["city"] = self.object.profile_contractor.city
            initial["region"] = self.object.profile_contractor.region
            initial["note"] = self.object.profile_contractor.note
            initial["company"] = self.object.profile_contractor.company

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["name_page"] = "Изменить данные клиента"
        context["name_btn"] = "Изменить"
        return context


class Account(LoginRequiredMixin, UpdateView):
    model = User
    fields = [
        "first_name",
        "last_name",
        "email",
        "email_notify",
        "telegram_notify",
    ]
    template_name = "users/account.html"
    extra_context = {
        "telegram_bot_url": settings.TG_BOT_URL,
    }

    def get_object(self, queryset=None):
        return self.request.user


class UpdateAvatar(LoginRequiredMixin, UpdateView):
    model = User
    fields = ["avatar"]
    template_name = "users/account.html"

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        super().form_valid(form)
        return JsonResponse({"avatar": self.object.avatar.url})


class GetUserByTokenView:
    def get(self, request, token):
        try:
            user = User.objects.get(token=token)
            return JsonResponse({"id": user.id, "first_name": user.first_name})
        except User.DoesNotExist:
            return JsonResponse({"id": None})


@method_decorator(csrf_exempt, name="dispatch")
class UpdateUserTelegamId(UpdateView):
    # csrf_exempt

    model = User
    fields = ["telegram_id"]
    template_name = "users/account.html"
    slug_url_kwarg = "token"
    slug_field = "token"

    def form_valid(self, form):
        self.object = form.save()
        self.object.telegram_notify = True
        self.object.save()
        super().form_valid(form)
        return JsonResponse(
            {"user": {"id": self.object.id, "first_name": self.object.first_name}}
        )

    def form_invalid(self, form):
        return JsonResponse({"user": None})
