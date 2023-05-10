import pytest
from django.urls import reverse

from users.models import Operator, User, ContractorProfile, Contractor


@pytest.mark.django_db
def test_create_user_customer(operator_factory, client):
    operator: User = operator_factory()
    url = reverse("customer-create")
    data = {"username": "operator-test", "email": "operator-test@gmail.com"}

    client.force_login(operator)
    res = client.post(url, data=data)

    assert res.status_code == 302
    operator = operator.get_role_user()
    assert operator.customers.count() == 1
    customer_created = operator.customers.first().user
    assert customer_created.email == data["email"]


class TestUpdateView:
    @pytest.mark.django_db
    def test_update_view_not_access_anonymous_user(self, client, customer_factory):
        customer = customer_factory()
        url = reverse("customer_edit", kwargs={"pk": customer.pk})
        res = client.get(url)
        assert res.status_code == 302

    @pytest.mark.django_db
    def test_update_view_not_access_customer(self, client, customer_factory):
        customer = customer_factory()
        url = reverse("customer_edit", kwargs={"pk": customer.pk})
        client.force_login(customer)
        res = client.get(url)
        assert res.status_code == 404

    @pytest.mark.django_db
    def test_update_view_access_operator(
        self, client, operator_factory, customer_factory
    ):
        operator = operator_factory()
        customer = customer_factory()
        customer.profile.linked_operators.add(operator)
        url = reverse("customer_edit", kwargs={"pk": customer.pk})
        client.force_login(operator)
        res = client.get(url)
        assert res.status_code == 200

    @pytest.mark.django_db
    def test_update_view_access_superuser(
        self, client, customer_factory, operator_factory
    ):
        admin = operator_factory(is_superuser=True)
        customer = customer_factory()
        url = reverse("customer_edit", kwargs={"pk": customer.pk})
        client.force_login(admin)
        res = client.get(url)
        assert res.status_code == 200

    @pytest.mark.django_db
    def test_update_view_not_access_operator_if_not_access_to_customer(
        self, client, operator_factory, customer_factory
    ):
        operator = operator_factory()
        customer = customer_factory()
        url = reverse("customer_edit", kwargs={"pk": customer.pk})
        client.force_login(operator)
        res = client.get(url)
        assert res.status_code == 404


class TestContractorView:
    @pytest.mark.django_db
    def test_update_view_contractor_save_city_region_and_note(
        self, user_factory, operator_factory, client
    ):
        contractor = user_factory(role=User.Role.CONTRACTOR)
        user = operator_factory()
        url = reverse("contractor_edit", kwargs={"pk": contractor.pk})
        data = {
            "username": "contractor-test",
            "email": "bla@email.com",
            "city": "city17",
            "region": "region17",
            "note": "note17",
        }
        client.force_login(user)
        res = client.post(url, data=data)
        assert res.status_code == 302
        profile = ContractorProfile.objects.first()
        assert profile.city == data["city"]
        assert profile.region == data["region"]
        assert profile.note == data["note"]

    @pytest.mark.django_db
    def test_create_contractor_with_all_field(self, operator_factory, client):
        operator = operator_factory()
        url = reverse("contractor-create")
        data = {
            "username": "contractor-test",
            "email": "bla@email.com",
            "city": "city17",
            "region": "region17",
            "note": "note17",
        }
        client.force_login(operator)
        res = client.post(url, data=data)
        assert res.status_code == 302
        contractor = Contractor.objects.get(username=data["username"])
        assert contractor
        assert contractor.profile_contractor.city == data["city"]
        assert contractor.profile_contractor.region == data["region"]
        assert contractor.profile_contractor.note == data["note"]


class TestAccountPage:
    @pytest.mark.django_db
    def test_account_page_exist(self, client, user_factory):
        user = user_factory()
        client.force_login(user)
        res = client.get(reverse("account"))
        assert res.status_code == 200
