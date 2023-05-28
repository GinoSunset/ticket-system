from django.views.generic import ListView
from .models import Manufacture


class ManufacturesListView(ListView):
    model = Manufacture
    template_name = "manufactures_list.html"
    context_object_name = "manufactures"
