from django.urls import path
from . import views

urlpatterns = [
    path("", views.ComponentListView.as_view(), name="component-list"),
    path(
        "create-component-type/",
        views.ComponentTypeCreateView.as_view(),
        name="component-type-create",
    ),
]
