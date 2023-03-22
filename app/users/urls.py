from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from users import views

urlpatterns = [
    path("update/", views.Account.as_view(), name="account"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("customer/", views.CreateCustomerView.as_view(), name="customer-create"),
    path("contractor/", views.CreateContractorView.as_view(), name="contractor-create"),
    path("customers/", views.ListCustomerView.as_view(), name="list-customers"),
    path("contractors/", views.ListContractorView.as_view(), name="list-contractors"),
    path(
        "contractors/json/",
        views.ListContractorJsonView.as_view(),
        name="contractor-list-ajax",
    ),
    path("customer/<int:pk>", views.UpdateCustomer.as_view(), name="customer_edit"),
    path(
        "contractor/<int:pk>",
        views.UpdateContractorView.as_view(),
        name="contractor_edit",
    ),
    path("update-avatar/", views.UpdateAvatar.as_view(), name="update-avatar"),
]
