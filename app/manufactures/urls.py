from django.urls import path
import manufactures.views as views


urlpatterns = [
    path("", views.ManufacturesListView.as_view(), name="manufactures-list"),
    path("create/", views.ManufactureCreateView.as_view(), name="manufactures-create"),
    path("<int:pk>/", views.ManufactureUpdateView.as_view(), name="manufacture-update"),
    path("client/create/", views.ClientCreateView.as_view(), name="client-create"),
    path(
        "nomenclature/create/",
        views.NomenclatureCreateView.as_view(),
        name="nomenclature-create",
    ),
    path(
        "<int:pk>/nomenclatures/",
        views.ManufactureNomenclaturesView.as_view(),
        name="manufacture-detail-nomenclatures",
    ),
]
