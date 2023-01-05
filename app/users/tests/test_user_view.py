import pytest
from django.urls import reverse

from users.models import Operator, User


@pytest.mark.django_db
def test_create_user_customer(operator_factory, client):
    operator: User = operator_factory()
    url = reverse("create-customer")
    data = {"username": "operator-test", "email": "operator-test@gmail.com"}

    client.force_login(operator)
    res = client.post(url, data=data)

    assert res.status_code == 302
    operator = operator.get_role_user()
    assert operator.customers.count() == 1
    customer_created = operator.customers.first().user
    assert customer_created.email == data["email"]
