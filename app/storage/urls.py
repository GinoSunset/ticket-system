from django.urls import path
from .views import component
from storage.views import component as c, delivery as d

urlpatterns = [
    path("", c.StorageListView.as_view(), name="storage"),
    path("search/", c.SearchView.as_view(), name="search"),
    path("component-list/", c.ComponentListView.as_view(), name="component-list"),
    path(
        "create-component-type/",
        c.ComponentTypeCreateView.as_view(),
        name="component-type-create",
    ),
    path(
        "create-component/",
        c.ComponentCreateView.as_view(),
        name="component-create",
    ),
    path(
        "component-type/<int:pk>/reserve/",
        c.ComponentTypeReserveView.as_view(),
        name="component-type-reserve",
    ),
    path(
        "nomenclature-components/<int:pk>/",
        c.NomenclatureComponents.as_view(),
        name="nomenclature-components",
    ),
    path("create-delivery/", d.CreateDelivery.as_view(), name="delivery-create"),
    path("get_deliveries/", d.DeliveryListView.as_view(), name="delivery-list"),
    path(
        "update_delivery/<int:pk>/",
        d.DeliveryUpdateView.as_view(),
        name="update_delivery",
    ),
    path(
        "done_delivery/<int:pk>/",
        d.DoneDelivery.as_view(),
        name="done_delivery",
    ),
    path("write-off/<int:pk>/", c.WriteOff.as_view(), name="write-off"),
    path(
        "create-delivery/<str:template>",
        d.GetDeliveryCreateTemplate.as_view(),
        name="delivery-template",
    ),
]
