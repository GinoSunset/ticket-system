from typing import Any, Dict
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DetailView,
    DeleteView,
)
from django.urls import reverse_lazy
from .models import Manufacture, Client, Nomenclature
from .forms import ManufactureForm, NomenclatureForm, ManufactureChangeStatusForm
from ticket.mixin import AccessOperatorMixin
from ticket.models import Ticket
from additionally.models import Dictionary


class ManufacturesListView(LoginRequiredMixin, ListView):
    model = Manufacture
    context_object_name = "manufactures"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["statuses"] = Dictionary.statuses_manufacture()
        return context


class ManufactureCreateView(AccessOperatorMixin, LoginRequiredMixin, CreateView):
    model = Manufacture
    form_class = ManufactureForm
    success_url = reverse_lazy("manufactures-list")

    def get_template_names(self) -> list[str]:
        if self.request.META.get("HTTP_HX_REQUEST"):
            return ["manufactures/htmx/ticket_field.html"]
        return super().get_template_names()

    def dispatch(self, request, *args, **kwargs):
        self.ticket = self.request.GET.get("ticket")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if self.ticket:
            self.ticket = Ticket.objects.get(pk=self.ticket)
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if ticket_pk := self.request.POST.get("ticket"):
            self.ticket = Ticket.objects.get(pk=ticket_pk)
        return super().post(request, *args, **kwargs)

    def get_success_url(self) -> str:
        if self.ticket:
            return reverse_lazy("ticket-update", kwargs={"pk": self.ticket.pk})
        return super().get_success_url()

    def get_context_data(self, form=None, forms_nomenclature=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.ticket:
            context["name_page"] = (
                f"Создание задачи на производство для задачи <a href='{reverse_lazy('ticket-update', args=[self.ticket.pk])}' >#{self.ticket.pk}</a>"
            )
        if forms_nomenclature:
            context["forms_nomenclature"] = forms_nomenclature
            context["count_form"] = len(forms_nomenclature) - 1
            return context
        context["count_form"] = 0
        forms_nomenclature = [NomenclatureForm(prefix="0")]
        context["forms_nomenclature"] = forms_nomenclature
        return context

    def get_initial(self):
        self.initial = super().get_initial()
        if self.ticket:
            self.initial.update(
                {
                    "ticket": self.ticket,
                    "comment": f"Для задачи #{self.ticket.pk} [{self.ticket.get_external_url()}]",
                }
            )
            if self.ticket.planned_execution_date:
                self.initial.update(
                    {"date_shipment": self.ticket.planned_execution_date}
                )
            self.initial.update()
        return self.initial

    def form_valid(self, form):
        form.instance.operator = self.request.user
        count_forms = int(self.request.POST["nomenclature-TOTAL_FORMS"])
        forms_nomenclature = []
        for i in range(count_forms + 1):
            form_nomenclature = NomenclatureForm(self.request.POST, prefix=str(i))
            forms_nomenclature.append(form_nomenclature)
        if not all([form_n.is_valid() for form_n in forms_nomenclature]):
            return self.render_to_response(
                self.get_context_data(form, forms_nomenclature=forms_nomenclature)
            )
        self.object = form.save()
        for form_nomenclature in forms_nomenclature:
            manufacture_nomenclature = form_nomenclature.save(commit=False)
            manufacture_nomenclature.manufacture = self.object
            manufacture_nomenclature.save()
            self.object.nomenclatures.add(manufacture_nomenclature)

        self.object.count = sum(
            [
                nomenclature.tx_count + nomenclature.rx_count
                for nomenclature in self.object.nomenclatures.all()
            ]
        )
        self.object.save()
        if self.ticket or form.cleaned_data.get("ticket"):
            message = f"Создана заявка на производство <a href='{self.object.get_absolute_url()}?ticket={self.ticket.pk}'>№{self.object.pk}</a>"
            self.ticket.create_update_system_comment(
                text=message, user=self.request.user
            )
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class ManufactureUpdateView(UpdateView):
    model = Manufacture
    form_class = ManufactureForm
    success_url = reverse_lazy("manufactures-list")

    def get_template_names(self) -> list[str]:
        if self.request.META.get("HTTP_HX_REQUEST"):
            return ["manufactures/htmx/ticket_field.html"]
        return super().get_template_names()

    def dispatch(self, request, *args, **kwargs):
        self.ticket = self.request.GET.get("ticket")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if self.ticket:
            self.ticket = Ticket.objects.get(pk=self.ticket)
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if ticket_pk := self.request.POST.get("ticket"):
            self.ticket = Ticket.objects.get(pk=ticket_pk)
        return super().post(request, *args, **kwargs)

    def get_context_data(self, form=None, forms_nomenclature=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["name_page"] = "Редактирование заявки на производство"
        context["name_btn"] = "Обновить"
        if forms_nomenclature:
            context["forms_nomenclature"] = forms_nomenclature
            context["count_form"] = len(forms_nomenclature) - 1
            return context
        count = self.object.nomenclatures.count()
        forms_nomenclature = []
        manufactory_nomenclatures = self.object.nomenclatures.all()
        for i, manufactory_nomenclature in enumerate(manufactory_nomenclatures):
            form = NomenclatureForm(prefix=str(i), instance=manufactory_nomenclature)
            forms_nomenclature.append(form)
        context["forms_nomenclature"] = forms_nomenclature
        context["count_form"] = count - 1  # -1 because first form is empty
        return context

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        count_forms = int(self.request.POST["nomenclature-TOTAL_FORMS"])

        forms_nomenclature = []
        for i in range(count_forms + 1):
            id_nomenclature = self.request.POST.get(f"{i}-id")
            instance_nomenclature = None
            if Nomenclature.objects.filter(id=id_nomenclature).exists():
                instance_nomenclature = Nomenclature.objects.get(id=id_nomenclature)
            form_nomenclature = NomenclatureForm(
                self.request.POST, prefix=str(i), instance=instance_nomenclature
            )
            forms_nomenclature.append(form_nomenclature)
        if not all([form_n.is_valid() for form_n in forms_nomenclature]):
            return self.render_to_response(
                self.get_context_data(form, forms_nomenclature=forms_nomenclature)
            )
        self.object = form.save()
        for form_nomenclature in forms_nomenclature:
            manufacture_nomenclature = form_nomenclature.save(commit=False)
            manufacture_nomenclature.manufacture = self.object
            manufacture_nomenclature.save()

        self.object.count = sum(
            [
                nomenclature.tx_count + nomenclature.rx_count
                for nomenclature in self.object.nomenclatures.all()
            ]
        )
        if "status" not in form.changed_data:
            self.object.status = self.get_status_from_nomenclatures()

        self.object.save()
        return super().form_valid(form)

    def get_status_from_nomenclatures(self):
        status_map = {
            1: Dictionary.objects.get(code="new_manufacture_task"),
            2: Dictionary.objects.get(code="in_progress"),
            3: Dictionary.objects.get(code="ready"),
            4: Dictionary.objects.get(code="shipped"),
            5: Dictionary.objects.get(code="canceled"),
        }
        min_status_nomenclature = min(
            [nomenclature.status for nomenclature in self.object.nomenclatures.all()],
            default=-1,
        )
        return status_map.get(min_status_nomenclature, self.object.status)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    fields = ["name", "comment"]
    success_url = reverse_lazy("manufactures-create")


class NomenclatureCreateView(LoginRequiredMixin, CreateView):
    model = Nomenclature
    form_class = NomenclatureForm
    success_url = reverse_lazy("manufactures-create")


class ManufactureNomenclaturesView(LoginRequiredMixin, DetailView):
    model = Manufacture
    template_name = "manufactures/manufacture_nomenclatures.html"
    context_object_name = "manufacture"
    queryset = Manufacture.objects.prefetch_related("nomenclatures")


class ManufactureStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Manufacture
    form_class = ManufactureChangeStatusForm
    success_url = reverse_lazy("manufactures-list")
    template_name = "manufactures/manufacture_change_status.html"

    def form_valid(self, form):
        self.object = form.save()
        if self.object.status.code in ["shipped", "ready", "canceled"]:
            # TODO: Переделать на update. Signal не срабатывает при update, нужно передать напрямую
            if self.object.status.code == "shipped":
                nomenclatures = self.object.nomenclatures.filter(
                    status__lte=Nomenclature.Status.SHIPPED
                )
                for nom in nomenclatures:
                    nom.status = Nomenclature.Status.SHIPPED
                    nom.save()
            elif self.object.status.code == "ready":
                nomenclatures = self.object.nomenclatures.filter(
                    status__lte=Nomenclature.Status.READY
                )
                for nom in nomenclatures:
                    nom.status = Nomenclature.Status.READY
                    nom.save()
            else:
                nomenclatures = self.object.nomenclatures.filter(
                    status__lte=Nomenclature.Status.CANCELED
                )
                for nom in nomenclatures:
                    nom.status = Nomenclature.Status.CANCELED
                    nom.save()

        return super().form_valid(form)


class ManufactureNomenclaturesPrintView(LoginRequiredMixin, DetailView):
    model = Manufacture
    template_name = "manufactures/manufacture_nomenclatures_print.html"
    context_object_name = "manufacture"
    queryset = Manufacture.objects.prefetch_related("nomenclatures")


class DeleteNomenclature(LoginRequiredMixin, DeleteView):
    model = Nomenclature
    success_url = reverse_lazy("manufactures-list")

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER", "/")
