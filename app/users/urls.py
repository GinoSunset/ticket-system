from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from .views import CreateCustomerView, ListCustomerView, UpdateCustomer

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("customer/", CreateCustomerView.as_view(), name="create-customer"),
    path("customers/", ListCustomerView.as_view(), name="list-customers"),
    path("customer/<int:pk>", UpdateCustomer.as_view(), name="customer_edit"),
]
