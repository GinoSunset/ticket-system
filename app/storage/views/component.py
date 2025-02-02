import logging
from typing import Any, Dict
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.db import models
from django.db.models import Count, Q
from django.views.generic import (
    ListView,
    CreateView,
    FormView,
    UpdateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.transaction import atomic
from django.forms.formsets import all_valid

from ticket.mixin import AccessOperatorMixin

from ..models import Component, ComponentType, TagComponent
from ..forms import (
    ComponentTypeForm,
    ComponentForm,
    ParentFormSet,
    WriteOffForm,
    ComponentSerialNumberFormSet,
)
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
        data["tags"] = TagComponent.objects.all()
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


class SearchView(StorageListView):
    model = Component
    template_name = "storage/table_body.html"
    context_object_name = "components"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        data = super().get_context_data(**kwargs)
        self._populate_context_data(data)
        return data

    def get_queryset(self):
        self._retrieve_request_params()
        components = self._get_filtered_queryset()
        return self._annotate_queryset(components)

    def _retrieve_request_params(self):
        self.search = self.request.GET.get("search")
        self.internal = self.request.GET.get("internal", False)
        self.tags = self.request.GET.getlist("tags")
        self.tags = [tag for tag in self.tags if tag]
        self.nomenclature_pk = self.request.GET.get("nomenclature_pk")

    def _get_filtered_queryset(self):
        components = Component.active_components.all()
        if self.search:
            components = components.filter(component_type__name__icontains=self.search)
        if self.nomenclature_pk:
            components = components.filter(nomenclature=self.nomenclature_pk)
        if not self.internal:
            components = components.filter(component_type__is_internal=False)
        if self.tags:
            for tag in self.tags:
                components = components.filter(component_type__tags__pk=tag)
        return components

    def _annotate_queryset(self, queryset):
        return queryset.values("component_type").annotate(
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

    def _populate_context_data(self, data: Dict[str, Any]):
        data["nomenclature_pk"] = self.request.GET.get("nomenclature_pk", False)
        if self.search:
            data["search"] = self.search
        if self.internal:
            data["internal"] = True
        if self.tags:
            data["tags"] = self.tags


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
        data["tags"] = TagComponent.objects.all()
        data["page_name"] = f"Компоненты номенклатуры №{self.kwargs.get('pk')}"
        nomenclature_pk = self.kwargs.get("pk")
        if nomenclature_pk:
            data["nomenclature_pk"] = nomenclature_pk
        return data

    def get_queryset(self):
        self.internal = self.request.GET.get("internal", False)
        nomenclature_pk = self.kwargs.get("pk")
        qs = Component.objects.all()
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

class UpdateComponentSerialNumber(AccessOperatorMixin, LoginRequiredMixin, UpdateView):
    model = Component
    template_name = "storage/htmx/modal_add_serial_number.html"
    success_url = reverse_lazy("storage:component_list")

    def get_queryset(self):
        self.component_type_pk = self.kwargs.get("pk")
        self.nomenclature_pk = self.kwargs.get("nomenclature_pk")
        return Component.objects.filter(
            nomenclature=self.nomenclature_pk, component_type=self.component_type_pk
        )

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        formset = ComponentSerialNumberFormSet(queryset=queryset)
        context = self.get_context(formset)
        return render(request, self.template_name, context)

    def get_context(self, formset):
        context = {}
        context["component_type"] = ComponentType.objects.get(pk=self.component_type_pk)
        context["nomenclature_pk"] = self.nomenclature_pk
        context["formset"] = formset
        return context

    def post(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        formset = ComponentSerialNumberFormSet(request.POST, queryset=queryset)
        context = self.get_context(formset)
        if formset.is_valid():
            formset.save()
            for form in formset:
                if form.has_changed():
                    component = form.instance
                    if not component.is_stock:
                        component.is_stock = True
                        logging.info(f"Component {component} is stock")
                    component.save()
                    logging.info(
                        f"Updated serial number for component {component.id}-{component.component_type} to {component.serial_number}, manufacture id {component.nomenclature.manufacture.id}"
                    )
            return render(request, self.template_name, context)
        return render(request, self.template_name, context, status=400)

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
