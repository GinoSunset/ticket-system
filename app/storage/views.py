from typing import Any
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


class ComponentByTypeListView(ListView):
    model = Component
    template_name = "storage/storage.html"
    context_object_name = "components"

    def get_queryset(self):
        return Component.objects.values("component_type").annotate(
            count=models.Count("component_type"),
            next_date_delivery=models.Min("date_delivery"),
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
