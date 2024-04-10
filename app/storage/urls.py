from django.urls import path
from . import views

urlpatterns = [
    path("", views.StorageListView.as_view(), name="storage"),
    path("search/", views.SearchView.as_view(), name="search"),
    path("component-list/", views.ComponentListView.as_view(), name="component-list"),
    path(
        "create-component-type/",
        views.ComponentTypeCreateView.as_view(),
        name="component-type-create",
    ),
    path(
        "create-component/",
        views.ComponentCreateView.as_view(),
        name="component-create",
    ),
    path(
        "component-type/<int:pk>/reserve/",
        views.ComponentTypeReserveView.as_view(),
        name="component-type-reserve",
    ),
    path(
        "nomenclature-components/<int:pk>/",
        views.NomenclatureComponents.as_view(),
        name="nomenclature-components",
    ),
    path(
        "create-delivery/", views.DeliveryCreateView.as_view(), name="delivery-create"
    ),
    path("get_deliveries/", views.DeliveryListView.as_view(), name="delivery-list"),
    path(
        "update_delivery/<int:pk>/",
        views.DeliveryUpdateView.as_view(),
        name="update_delivery",
    ),
    path(
        "done_delivery/<int:pk>/",
        views.DoneDelivery.as_view(),
        name="done_delivery",
    ),
    path("write-off/<int:pk>/", views.WriteOff.as_view(), name="write-off"),
]
