import pytest
from users.models import Customer, Contractor, Operator, User


@pytest.mark.django_db
def test_create_customer_return_customer():
    user: Customer = Customer.objects.create(username="test", password="test")
    assert user.role == User.Role.CUSTOMER


@pytest.mark.django_db
def test_create_contractor_return_contractor():
    user: Contractor = Contractor.objects.create(username="test", password="test")
    assert user.role == User.Role.CONTRACTOR


@pytest.mark.django_db
def test_create_operator_return_operator():
    user: Operator = Operator.objects.create(username="test", password="test")
    assert user.role == User.Role.OPERATOR


@pytest.mark.django_db
def test_contractor_has_city_and_region():
    user: Contractor = Contractor.objects.create(username="test", password="test")
    assert hasattr(user.profile_contractor, "city")
    assert hasattr(user.profile_contractor, "region")
