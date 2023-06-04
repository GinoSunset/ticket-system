from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Manufacture, Client, Nomenclature
from .forms import ManufactureForm, ManufactureNomenclatureForm


class ManufacturesListView(ListView):
    model = Manufacture
    context_object_name = "manufactures"


class ManufactureCreateView(CreateView):
    model = Manufacture
    form_class = ManufactureForm
    success_url = reverse_lazy("manufactures-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_nomenclature"] = ManufactureNomenclatureForm(prefix="0")
        return context

    def form_valid(self, form):
        form.instance.operator = self.request.user
        count_forms = int(self.request.POST["nomenclature-TOTAL_FORMS"])
        self.object = form.save()
        for i in range(count_forms + 1):
            form_nomenclature = ManufactureNomenclatureForm(
                self.request.POST, prefix=str(i)
            )
            if form_nomenclature.is_valid():
                manufacture_nomenclature = form_nomenclature.save(commit=False)
                manufacture_nomenclature.manufacture = self.object
                manufacture_nomenclature.save()
            else:
                return super().form_invalid(form)
        return super().form_valid(form)


class ManufactureUpdateView(UpdateView):
    model = Manufacture
    form_class = ManufactureForm
    success_url = reverse_lazy("manufactures-list")


class ClientCreateView(CreateView):
    model = Client
    fields = ["name", "comment"]
    success_url = reverse_lazy("manufactures-create")


class NomenclatureCreateView(CreateView):
    model = Nomenclature
    fields = ["name", "description"]
    success_url = reverse_lazy("manufactures-create")
