from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from .views import (
    CreateCustomerView,
    ListContractorView,
    ListCustomerView,
    UpdateCustomer,
    CreateContractorView,
    UpdateContractorView,
)

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("customer/", CreateCustomerView.as_view(), name="customer-create"),
    path("contractor/", CreateContractorView.as_view(), name="contractor-create"),
    path("customers/", ListCustomerView.as_view(), name="list-customers"),
    path("contractors/", ListContractorView.as_view(), name="list-contractors"),
    path("customer/<int:pk>", UpdateCustomer.as_view(), name="customer_edit"),
    path("contractor/<int:pk>", UpdateContractorView.as_view(), name="contractor_edit"),
]
