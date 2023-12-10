from typing import Any
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from .models import Component, ComponentType, Alias
from .forms import AliasFormSet, ComponentTypeForm


class ComponentListView(ListView):
    model = Component
    template_name = "storage/component_list.html"
    context_object_name = "components"


class ComponentTypeCreateView(CreateView):
    model = ComponentType
    template_name = "storage/component_type_create.html"
    form_class = ComponentTypeForm
    success_url = reverse_lazy("component-list")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["aliases_formset"] = AliasFormSet(
                self.request.POST, prefix="aliases"
            )
            return context
        context["aliases_formset"] = AliasFormSet(prefix="aliases")
        return context

    def form_valid(self, form):
        aliases = form.data["alias"].split(",")
        component_type = form.save()
        for alias_name in aliases:
            Alias.objects.get_or_create(name=alias_name, component_type=component_type)
        return super().form_valid(form)
