import datetime
import logging
from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.db.transaction import atomic
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.forms.formsets import all_valid
from django.forms import modelformset_factory
from django.db import models
from django.db.models import Q

from ticsys.utils import is_htmx
from ticket.mixin import AccessOperatorMixin
from storage.models import (
    Delivery,
    Component,
    ComponentType,
    Invoice,
    Alias,
    InvoiceAliasRelation,
)
from storage.forms import (
    DeliveryForm,
    DeliveryInvoiceForm,
    TypeComponentCountFormSet,
    AliasInvoiceForm,
)
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    FormView,
    DeleteView,
)


class CreateDelivery(AccessOperatorMixin, LoginRequiredMixin, CreateView):
    model = Delivery
    template_name = "storage/delivery_create.html"
    form_class = DeliveryForm
    success_url = reverse_lazy("storage")

    def get_template_names(self) -> list[str]:
        if is_htmx(self.request):
            return ["storage/htmx/manual_delivery.html"]
        return super().get_template_names()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        kwargs = super().get_context_data(**kwargs)
        if "type_count_forms" not in kwargs:
            kwargs["type_count_forms"] = TypeComponentCountFormSet(prefix="type_count")
        return kwargs

    @atomic()
    def form_valid(self, form):
        self.object: Delivery = form.save(commit=False)
        self.object.status = Delivery.Status.NEW
        self.object.save()
        type_count_forms = TypeComponentCountFormSet(
            self.request.POST, prefix="type_count"
        )
        if not all_valid(type_count_forms):
            self.object.delete()
            return self.render_to_response(
                self.get_context_data(form=form, type_count_forms=type_count_forms)
            )

        for type_count_form in type_count_forms:
            count = type_count_form.cleaned_data["count"]
            cmnt_type = type_count_form.cleaned_data["component_type"]
            create_delivery_component(self.object, count, cmnt_type)
            # TODO: logging

        return super().form_valid(form)


class DeliveryListView(AccessOperatorMixin, LoginRequiredMixin, ListView):
    model = Delivery
    template_name = "storage/include/list_delivery.html"
    context_object_name = "delivers"
    ordering = ["date_delivery"]
    queryset = Delivery.objects.filter(Q(status=Delivery.Status.NEW)|Q(status=Delivery.Status.DRAFT))


class DeliveryUpdateView(AccessOperatorMixin, LoginRequiredMixin, UpdateView):
    model = Delivery
    template_name = "storage/delivery_create.html"
    form_class = DeliveryForm
    success_url = reverse_lazy("storage")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        kwargs = super().get_context_data(**kwargs)
        kwargs["name_page"] = "Редактирование доставки"
        kwargs["is_update_delivery"] = True
        kwargs["name_btn"] = "Обновить"
        if "type_count_forms" not in kwargs:
            cts = (
                Component.objects.filter(delivery=self.object)
                .values("component_type")
                .annotate(count=models.Count("component_type"))
            )

            kwargs["type_count_forms"] = TypeComponentCountFormSet(
                initial=cts, prefix="type_count"
            )
        return kwargs

    def form_valid(self, form):
        type_count_forms = TypeComponentCountFormSet(
            self.request.POST, prefix="type_count"
        )
        if not all_valid(type_count_forms):
            return self.render_to_response(
                self.get_context_data(form=form, type_count_forms=type_count_forms)
            )
        for type_count_form in type_count_forms:
            count = type_count_form.cleaned_data["count"]
            cmnt_type = type_count_form.cleaned_data["component_type"]
            self.change_if_needed(self.object, cmnt_type, count)
        return super().form_valid(form)

    @staticmethod
    def change_if_needed(delivery: Delivery, cmnt_type: ComponentType, count: int):
        count_in_db = Component.objects.filter(
            delivery=delivery,
            component_type=cmnt_type,
        ).count()
        if count_in_db > count:
            DeliveryUpdateView.remove_component_delivery(
                delivery, cmnt_type, count, count_in_db
            )
            return
        if count_in_db < count:
            DeliveryUpdateView.added_component_delivery(
                delivery, cmnt_type, count, count_in_db
            )

    @staticmethod
    def added_component_delivery(delivery, cmnt_type, count, count_in_db):
        count_added = count - count_in_db
        create_delivery_component(
            delivery=delivery, cmnt_type=cmnt_type, count=count_added
        )

    @staticmethod
    def remove_component_delivery(delivery, cmnt_type, count, count_in_db):
        count_for_delete = count_in_db - count
        components_for_delete = Component.objects.filter(
            delivery=delivery,
            component_type=cmnt_type,
        ).order_by("-pk")[:count_for_delete]
        for component_for_delete in components_for_delete:
            if component_for_delete.nomenclature is not None:
                component_for_delete.delivery = None
                component_for_delete.date_delivery = None
                component_for_delete.save()
                continue
            component_for_delete.delete()


class DoneDelivery(AccessOperatorMixin, LoginRequiredMixin, UpdateView):
    model = Delivery

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()
        self.today = datetime.date.today()

        self.update_delivery()
        return HttpResponse(status=201)

    def add_to_stock_component_delivery(self):
        logging.info(f"delivery {self.object.pk} changed to done")
        Component.objects.filter(delivery=self.object, is_reserve=True).update(
            date_delivery=self.today, is_stock=True
        )
        free_components = Component.objects.filter(delivery=self.object).exclude(
            is_reserve=True
        )
        for free_component in free_components:
            component = Component.objects.filter(
                component_type=free_component.component_type,
                delivery__isnull=True,
                is_stock=False,
                is_reserve=True,
                date_delivery__isnull=True,
            ).first()
            if component:
                component.delivery = self.object
                component.date_delivery = self.today
                component.is_stock = True
                component.save()
                logging.info(
                    f"{free_component.pk=} change to {component} from delivery and was reserve when delivery #{self.object.pk} done"
                )
                free_component.delete()
                continue
            free_component.date_delivery = self.today
            free_component.is_stock = True
            logging.info(
                f"{free_component.pk=} added to stock when delivery #{self.object.pk} done"
            )
            free_component.save()

    @atomic
    def update_delivery(self):
        self.object.status = Delivery.Status.DONE
        if self.object.date_delivery != self.today:
            self.object.date_delivery = self.today
        self.add_to_stock_component_delivery()
        self.object.save()


def create_delivery_component(delivery: Delivery, count: int, cmnt_type: ComponentType):
    date_delivery = delivery.date_delivery
    for _ in range(count):
        # TODO: don't search always free component, if not set bool flag
        # TODO: check than component in stock without delivery was add delivery.!
        component = Component.objects.filter(
            component_type=cmnt_type,
            nomenclature__manufacture__date_shipment__gte=date_delivery,
            delivery__isnull=True,
            date_delivery__isnull=True,
        ).first()
        if not component:
            component = Component.objects.create(
                component_type=cmnt_type,
            )
            logging.info(
                f"{component.component_type} was create by delivery {delivery}"
            )

        component.date_delivery = delivery.date_delivery
        component.delivery = delivery
        component.save()
        logging.info(f"{component} was added  delivery {delivery}")


class GetDeliveryCreateTemplate(FormView):
    template_name = "storage/htmx/auto_delivery.html"


class CreateDeliveryThrowInvoice(AccessOperatorMixin, LoginRequiredMixin, CreateView):
    model = Delivery
    template_name = "storage/delivery_create.html"
    form_class = DeliveryInvoiceForm
    success_url = reverse_lazy("storage")  # TODO: change me

    def get_template_names(self) -> list[str]:
        if is_htmx(self.request):
            return ["storage/htmx/auto_delivery.html"]
        return super().get_template_names()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        kwargs = super().get_context_data(**kwargs)
        kwargs["is_invoice_delivery"] = True
        if "type_count_forms" not in kwargs:
            kwargs["type_count_forms"] = TypeComponentCountFormSet(prefix="type_count")
        return kwargs

    @atomic()
    def form_valid(self, form):
        self.object: Delivery = form.save(commit=False)
        self.object.status = Delivery.Status.DRAFT
        self.object.save()
        form.save()
        self.object.invoice.to_work()
        return HttpResponseRedirect(self.get_success_url())

class UpdateInvoice(AccessOperatorMixin, LoginRequiredMixin, UpdateView):
    model = Delivery
    template_name = "storage/update_invoice.html"
    form_class = DeliveryForm
    success_url = reverse_lazy("storage")


    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        data = super().get_context_data(**kwargs)
        formset = self.get_formset()
        if data.get("alias_invoice_forms") is None:
            data.update({"alias_invoice_forms": formset})
        return data

    def get_formset(self):
        initial_forms = self.get_initial_for_alias_invoice()
        ids_alias = set([i.get("id") for i in initial_forms])
        AliasInvoiceFormSet = self.create_formset()
        formset = AliasInvoiceFormSet(queryset=Alias.objects.filter(id__in=ids_alias))

        for form, initial_data in zip(formset.forms, initial_forms):
            form.initial.update(initial_data)
        return formset
    

    def create_formset(self, min_num=1):
        return modelformset_factory(
            Alias, form=AliasInvoiceForm, min_num=min_num, validate_min=True, extra=0
        )


    def get_initial_for_alias_invoice(self):
        initial_forms = []
        alias_invoices = self.object.invoice.invoice.all()
        for i in alias_invoices:
            name = 'Unknow' if i.alias is None else i.alias.name
            id_ = None if i.alias is None else i.alias.pk
            init_data = {
                "name": name,
                "quantity": i.quantity,
                "id": id_,
                "id_relation": i.pk,
            }
            if i.alias and i.alias.component_type is not None:
                init_data.update({"component_type": i.alias.component_type})
            initial_forms.append(init_data)
        return initial_forms

    @atomic()
    def form_valid(self, form):
        self.object: Delivery = form.save(commit=False)
        # TODO: to_new

        AliasInvoiceFormSet = self.create_formset()
        alias_invoice_forms = AliasInvoiceFormSet(self.request.POST)
        initial_forms = self.get_initial_for_alias_invoice()
        for alias_form, initial_data in zip(alias_invoice_forms.forms, initial_forms):
            alias_form.initial.update(initial_data)
        if not all_valid(alias_invoice_forms):
            return self.render_to_response(
                self.get_context_data(form=form, alias_invoice_forms=alias_invoice_forms)
            )
        
        self.object.status = Delivery.Status.NEW
        self.object.save()
        for type_quantity_form in alias_invoice_forms:
            type_quantity_form.save()
            quantity = type_quantity_form.cleaned_data["quantity"]
            cmnt_type = type_quantity_form.cleaned_data["component_type"]
            create_delivery_component(self.object, quantity, cmnt_type)
            # TODO: logging

        return super().form_valid(form)


class InvoiceAliasDeleteView(AccessOperatorMixin, LoginRequiredMixin, DeleteView):
    model = InvoiceAliasRelation

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return HttpResponse(status=200)
