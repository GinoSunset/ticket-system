from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Manufacture, Client, Nomenclature
from .forms import ManufactureForm, NomenclatureForm
from ticket.mixin import AccessOperatorMixin
import logging


class ManufacturesListView(LoginRequiredMixin, ListView):
    model = Manufacture
    context_object_name = "manufactures"


class ManufactureCreateView(AccessOperatorMixin, LoginRequiredMixin, CreateView):
    model = Manufacture
    form_class = ManufactureForm
    success_url = reverse_lazy("manufactures-list")

    def form_valid(self, form):
        form.instance.operator = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        logging.info(f"form_invalid. POST: {self.request.POST}, form: {form}, ")
        return self.render_to_response(self.get_context_data(form=form))


class ManufactureUpdateView(LoginRequiredMixin, UpdateView):
    model = Manufacture
    form_class = ManufactureForm
    success_url = reverse_lazy("manufactures-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["name_page"] = "Редактирование заявки на производство"
        context["name_btn"] = "Обновить"
        return context


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    fields = ["name", "comment"]
    success_url = reverse_lazy("manufactures-create")


class NomenclatureCreateView(LoginRequiredMixin, CreateView):
    model = Nomenclature
    form_class = NomenclatureForm
    success_url = reverse_lazy("manufactures-create")
