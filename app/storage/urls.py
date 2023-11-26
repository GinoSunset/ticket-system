from django.urls import path
from . import views

urlpatterns = [
    path("", views.ComponentListView.as_view(), name="component-list"),
]
