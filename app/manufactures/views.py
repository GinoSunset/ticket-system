from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Manufacture, Client
from .forms import ManufactureForm


class ManufacturesListView(ListView):
    model = Manufacture
    context_object_name = "manufactures"


class ManufactureCreateView(CreateView):
    model = Manufacture
    form_class = ManufactureForm
    success_url = reverse_lazy("manufactures-list")

    def form_valid(self, form):
        form.instance.operator = self.request.user
        return super().form_valid(form)


class ManufactureUpdateView(UpdateView):
    model = Manufacture
    form_class = ManufactureForm
    success_url = reverse_lazy("manufactures-list")


class ClientCreateView(CreateView):
    model = Client
    fields = ["name", "comment"]
    success_url = reverse_lazy("manufactures-create")
