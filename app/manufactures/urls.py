from django.urls import path
import manufactures.views as views


urlpatterns = [
    path("", views.ManufacturesListView.as_view(), name="manufactures-list"),
]
