from django.urls import path
from . import views

urlpatterns = [
    path("", views.StorageListView.as_view(), name="storage"),
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
]
