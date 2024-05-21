import datetime
import logging
from typing import Any
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.db import models
from django.db.models import Count, Q
from django.views.generic import ListView, CreateView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.transaction import atomic
from django.forms.formsets import all_valid, formset_factory

from ticket.mixin import AccessOperatorMixin

from .models import Component, ComponentType, Alias, Delivery
from .forms import (
    ComponentTypeForm,
    ComponentForm,
    ParentFormSet,
    DeliveryForm,
    TypeComponentCountFormSet,
    TypeComponentCountForm,
    WriteOffForm,
)
from .reserve import reserve_component
from django.shortcuts import redirect


class ComponentListView(AccessOperatorMixin, LoginRequiredMixin, ListView):
    model = Component
    template_name = "storage/component_list_all.html"
    context_object_name = "components"
    ordering = ["component_type", "-id"]

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return redirect("manufactures-list")

        # return super().get(request, *args, **kwargs)


class StorageListView(AccessOperatorMixin, LoginRequiredMixin, ListView):
    model = Component
    template_name = "storage/storage.html"
    context_object_name = "components"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        data = super().get_context_data(**kwargs)
        data["nomenclature_pk"] = False
        return data

    def get_queryset(self):
        components = Component.active_components.all()
        internal = self.request.GET.get("internal", False)
        if not internal:
            components = components.filter(component_type__is_internal=False)

        return components.values(
            "component_type",
        ).annotate(
            count=models.Count("component_type"),
            component_type_name=models.F("component_type__name"),
            in_stock=models.Sum(
                models.Case(
                    models.When(is_stock=True, then=1),
                    default=0,
                    output_field=models.IntegerField(),
                )
            ),
            in_reserve=models.Sum(
                models.Case(
                    models.When(is_reserve=True, then=1),
                    default=0,
                    output_field=models.IntegerField(),
                )
            ),
            in_delivery=models.Sum(
                models.Case(
                    models.When(
                        models.Q(is_stock=False)
                        & models.Q(date_delivery__isnull=False),
                        then=1,
                    ),
                    default=0,
                    output_field=models.IntegerField(),
                )
            ),
        )


class SearchView(AccessOperatorMixin, LoginRequiredMixin, ListView):
    model = Component
    template_name = "storage/table_body.html"
    context_object_name = "components"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        data = super().get_context_data(**kwargs)

        data["nomenclature_pk"] = self.request.GET.get("nomenclature_pk", False)
        if self.search:
            data["search"] = self.search
        if self.internal:
            data["internal"] = True
        return data

    def get_queryset(self):
        self.search = self.request.GET.get("search")
        self.internal = self.request.GET.get("internal", False)
        nomenclature_pk = self.request.GET.get("nomenclature_pk")

        components = Component.active_components.all()
        if self.search:
            components = Component.active_components.filter(
                component_type__name__icontains=self.search
            )
        if nomenclature_pk:
            components = components.filter(nomenclature=nomenclature_pk)
        if not self.internal:
            components = components.filter(component_type__is_internal=False)
        return components.values(
            "component_type",
        ).annotate(
            count=models.Count("component_type"),
            component_type_name=models.F("component_type__name"),
            in_stock=models.Sum(
                models.Case(
                    models.When(is_stock=True, then=1),
                    default=0,
                    output_field=models.IntegerField(),
                )
            ),
            in_reserve=models.Sum(
                models.Case(
                    models.When(is_reserve=True, then=1),
                    default=0,
                    output_field=models.IntegerField(),
                )
            ),
            in_delivery=models.Sum(
                models.Case(
                    models.When(
                        models.Q(is_stock=False)
                        & models.Q(date_delivery__isnull=False),
                        then=1,
                    ),
                    default=0,
                    output_field=models.IntegerField(),
                )
            ),
        )


class ComponentTypeCreateView(AccessOperatorMixin, LoginRequiredMixin, CreateView):
    model = ComponentType
    template_name = "storage/component_type_create.html"
    form_class = ComponentTypeForm
    success_url = reverse_lazy("storage")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "parent_forms" not in kwargs:
            context["parent_forms"] = ParentFormSet(prefix="parents")
        return context

    @atomic()
    def form_valid(self, form):
        self.object = form.save()
        parent_forms = ParentFormSet(self.request.POST, prefix="parents")
        if not all_valid(parent_forms):
            self.object.delete()
            return self.render_to_response(
                self.get_context_data(form=form, parent_forms=parent_forms)
            )

        for parent_form in parent_forms:
            parrent = parent_form.save(commit=False)
            parrent.sub_component_type = self.object
            parrent.save()

        return super().form_valid(form)


class ComponentCreateView(AccessOperatorMixin, LoginRequiredMixin, CreateView):
    model = Component
    template_name = "storage/component_create.html"
    form_class = ComponentForm
    success_url = reverse_lazy("storage")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        component_type_id = self.request.GET.get("component_type")
        if component_type_id:
            component_type = get_object_or_404(ComponentType, id=component_type_id)
            kwargs["initial"]["component_type"] = component_type
        return kwargs

    def update_component(
        self,
        component,
        is_stock=False,
        serial_number=None,
        date_delivery=None,
    ):
        component.is_stock = is_stock
        if serial_number:
            component.serial_number = serial_number
        if date_delivery:
            component.date_delivery = date_delivery
        component.save()
        return component

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        count = form.cleaned_data["count"]
        generate_serial_number = form.cleaned_data["generate_serial_number"]
        serial_number = None

        count_create_component = count
        for _ in range(count):
            if generate_serial_number:
                serial_number = Component.generate_serial_number(
                    form.cleaned_data["component_type"]
                )
            result = self.reserve_exist_component(
                form,
                serial_number,
            )
            if result:
                count_create_component -= 1

        for _ in range(count_create_component):
            if generate_serial_number:
                form.instance.serial_number = Component.generate_serial_number(
                    form.cleaned_data["component_type"]
                )
            if self.object and self.object.pk:
                self.object.pk = None
            self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def reserve_exist_component(
        self,
        form,
        serial_number,
    ):
        component_type = form.cleaned_data["component_type"]
        is_stock = form.cleaned_data["is_stock"]
        date_delivery = form.cleaned_data["date_delivery"]
        components_to_reserve = None

        if is_stock:
            components_to_reserve = self.get_components_to_reserve(component_type)

        if date_delivery:
            components_to_reserve = self.get_components_to_reserve_by_date_delivery(
                component_type, date_delivery
            )

        if components_to_reserve and components_to_reserve.exists():
            component = components_to_reserve.first()
            component = self.update_component(
                component,
                is_stock,
                serial_number,
                date_delivery,
            )
            self.object = component
            return True
        return False

    def get_components_to_reserve(self, component_type):
        # TODO: do this method to model
        return Component.active_components.filter(
            component_type=component_type,
            is_reserve=True,
            is_stock=False,
            date_delivery__isnull=True,
        )

    def get_components_to_reserve_by_date_delivery(self, component_type, date_delivery):
        # TODO: do this method to model
        return Component.active_components.filter(
            component_type=component_type,
            is_reserve=True,
            is_stock=False,
            nomenclature__manufacture__date_shipment__gte=date_delivery,
            date_delivery__isnull=True,
        )


class ComponentTypeReserveView(AccessOperatorMixin, LoginRequiredMixin, ListView):
    model = ComponentType
    template_name = "storage/component_type_modal.html"
    context_object_name = "manufacturers"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["component_type"] = ComponentType.objects.get(pk=self.kwargs.get("pk"))
        return context

    def get_queryset(self):
        componentType = ComponentType.objects.get(id=self.kwargs["pk"])
        manufactures = (
            Component.active_components.filter(
                component_type=componentType, is_reserve=True
            )
            .values(
                "nomenclature__manufacture",
                "nomenclature__manufacture__date_shipment",
                "nomenclature__manufacture__client__name",
            )
            .annotate(
                id=models.F("nomenclature__manufacture"),
                date_shipment=models.F("nomenclature__manufacture__date_shipment"),
                client=models.F("nomenclature__manufacture__client__name"),
                count=Count("id"),
            )
            .exclude(
                Q(
                    nomenclature__manufacture__status__code__in=[
                        "canceled",
                        "ready",
                        "shipped",
                    ]
                )
            )
        )

        # get all manufacture from nomenclatures with distinct
        return manufactures


class NomenclatureComponents(AccessOperatorMixin, LoginRequiredMixin, ListView):
    model = Component
    template_name = "storage/component_list.html"
    context_object_name = "components"
    ordering = ["component_type", "-id"]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        data = super().get_context_data(**kwargs)
        data["page_name"] = f"Компоненты номенклатуры №{self.kwargs.get('pk')}"
        nomenclature_pk = self.kwargs.get("pk")
        if nomenclature_pk:
            data["nomenclature_pk"] = nomenclature_pk
        return data

    def get_queryset(self):
        self.internal = self.request.GET.get("internal", False)
        nomenclature_pk = self.kwargs.get("pk")
        qs = Component.active_components.all()
        if nomenclature_pk:
            qs = qs.filter(nomenclature=nomenclature_pk)
        if not self.internal:
            qs = qs.filter(component_type__is_internal=False)
        return qs.values(
            "component_type",
        ).annotate(
            count=models.Count("component_type"),
            component_type_name=models.F("component_type__name"),
            in_stock=models.Sum(
                models.Case(
                    models.When(is_stock=True, then=1),
                    default=0,
                    output_field=models.IntegerField(),
                )
            ),
            in_reserve=models.Sum(
                models.Case(
                    models.When(is_reserve=True, then=1),
                    default=0,
                    output_field=models.IntegerField(),
                )
            ),
            in_delivery=models.Sum(
                models.Case(
                    models.When(
                        models.Q(is_stock=False)
                        & models.Q(date_delivery__isnull=False),
                        then=1,
                    ),
                    default=0,
                    output_field=models.IntegerField(),
                )
            ),
        )


class DeliveryCreateView(AccessOperatorMixin, LoginRequiredMixin, CreateView):
    model = Delivery
    template_name = "storage/delivery_create.html"
    form_class = DeliveryForm
    success_url = reverse_lazy("storage")

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
    queryset = Delivery.objects.filter(status=Delivery.Status.NEW)


class DeliveryUpdateView(AccessOperatorMixin, LoginRequiredMixin, UpdateView):
    model = Delivery
    template_name = "storage/delivery_create.html"
    form_class = DeliveryForm
    success_url = reverse_lazy("storage")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        kwargs = super().get_context_data(**kwargs)
        kwargs["name_page"] = "Редактирование доставки"
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
                free_component.delete()
                continue
            free_component.date_delivery = self.today
            free_component.is_stock = True
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


class WriteOff(AccessOperatorMixin, LoginRequiredMixin, FormView):
    form_class = WriteOffForm
    template_name = "storage/write_off_form.html"
    template_post_name = "storage/in_stock_row.html"

    def get_initial(self):
        """Return the initial data to use for forms on this view."""
        self.initial = {
            "component_type": self.kwargs["pk"]
        }  # ComponentType.objects.get(self.kwargs["pk"])}
        return self.initial.copy()

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs["in_stock"] = Component.active_components.filter(
            component_type__pk=self.kwargs["pk"], is_stock=True
        ).count()
        kwargs["component_type_id"] = self.kwargs["pk"]
        return kwargs

    def form_valid(self, form):
        ct = form.cleaned_data["component_type"]
        count_to_delete = form.cleaned_data["count_write_off"]
        count_deleted = self.remove_free_components(ct, count_to_delete)
        in_stock = Component.active_components.filter(
            component_type=ct, is_stock=True
        ).count()

        return self.render_to_response(self.get_context_data(form=form))

    def remove_free_components(self, ct: ComponentType, count_to_delete: int):
        component_for_delete = Component.active_components.filter(
            component_type=ct, is_reserve=False, is_stock=True
        )[:count_to_delete]

        count_deleted = component_for_delete.count()
        [component.delete() for component in component_for_delete]

        logging.info(
            f"Write off {component_for_delete} {ct} - {component_for_delete.count()} "
        )
        return count_deleted

    def form_invalid(self, form):
        response = super().form_invalid(form)
        return response

    def get_template_names(self):
        if self.request.method == "POST":
            return [self.template_post_name]
        return super().get_template_names()
