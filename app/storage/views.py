from django.shortcuts import render
from django.views.generic import ListView
from .models import Component


class ComponentListView(ListView):
    model = Component
    template_name = "storage/component_list.html"
    context_object_name = "components"
