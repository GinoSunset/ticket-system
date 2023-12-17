from typing import Any
from django.forms.models import BaseModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.db import models
from django.views.generic import ListView, CreateView
from .models import Component, ComponentType, Alias
from .forms import ComponentTypeForm, ComponentForm


class ComponentListView(ListView):
    model = Component
    template_name = "storage/component_list.html"
    context_object_name = "components"


class StorageListView(ListView):
    model = Component
    template_name = "storage/storage.html"
    context_object_name = "components"

    def get_queryset(self):
        return Component.objects.values(
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


class ComponentTypeCreateView(CreateView):
    model = ComponentType
    template_name = "storage/component_type_create.html"
    form_class = ComponentTypeForm
    success_url = reverse_lazy("component-list")


class ComponentCreateView(CreateView):
    model = Component
    template_name = "storage/component_create.html"
    form_class = ComponentForm
    success_url = reverse_lazy("component-list")

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        component_type = form.cleaned_data["component_type"]
        if form.cleaned_data["is_stock"]:
            component_to_reserve = self.get_component_to_reserve(component_type)
            if component_to_reserve.exists():
                component: Component = component_to_reserve.first()
                component.is_stock = True
                if serial_number := form.cleaned_data["serial_number"]:
                    component.serial_number = serial_number
                if date_delivery := form.cleaned_data["date_delivery"]:
                    component.date_delivery = date_delivery
                component.save()
                self.object = component
                return HttpResponseRedirect(self.get_success_url())
        if date_delivery := form.cleaned_data["date_delivery"]:
            # TODO: this if and higher if is the same
            component_to_reserve = self.get_component_to_reserve_by_date_delivery(
                component_type, date_delivery
            )
            if component_to_reserve.exists():
                component: Component = component_to_reserve.first()
                if date_delivery := form.cleaned_data["date_delivery"]:
                    component.date_delivery = date_delivery
                if serial_number := form.cleaned_data["serial_number"]:
                    component.serial_number = serial_number
                component.save()
                self.object = component
                return HttpResponseRedirect(self.get_success_url())
        return super().form_valid(form)

    def get_component_to_reserve(self, component_type):
        # TODO: do this method to model
        return Component.objects.filter(
            component_type=component_type,
            is_reserve=True,
            is_stock=False,
            date_delivery__isnull=True,
        )

    def get_component_to_reserve_by_date_delivery(self, component_type, date_delivery):
        # TODO: do this method to model
        return Component.objects.filter(
            component_type=component_type,
            is_reserve=True,
            is_stock=False,
            nomenclature__manufacture__date_shipment__gte=date_delivery,
            date_delivery__isnull=True,
        )


class ComponentTypeReserveView(ListView):
    model = ComponentType
    template_name = "storage/component_type_modal.html"
    context_object_name = "manufacturers"

    def get_queryset(self):
        componentType = ComponentType.objects.get(id=self.kwargs["pk"])
        manufactures = (
            Component.objects.filter(component_type=componentType, is_reserve=True)
            .values(
                "nomenclature__manufacture",
                "nomenclature__manufacture__date_shipment",
                "nomenclature__manufacture__client__name",
            )
            .distinct()
            .annotate(
                id=models.F("nomenclature__manufacture"),
                date_shipment=models.F("nomenclature__manufacture__date_shipment"),
                client=models.F("nomenclature__manufacture__client__name"),
            )
        )

        # get all manufacture from nomenclatures with distinct
        return manufactures
