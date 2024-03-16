import pytest
from django.urls import reverse

PAGES_URLS_PARAMS = [
    ("storage", False),
    ("component-list", False),
    ("nomenclature-components", True),
    ("component-type-create", False),
    ("component-create", False),
    ("component-type-reserve", True),
]


@pytest.mark.django_db
@pytest.mark.parametrize("page, is_has_params", PAGES_URLS_PARAMS)
def test_anonymous_user_has_no_access(client, component_factory, page, is_has_params):
    component = component_factory()
    kwargs = {"pk": component.pk} if is_has_params else {}
    url = reverse(page, kwargs=kwargs)

    response = client.get(url)

    assert response.status_code == 302


@pytest.mark.django_db
@pytest.mark.parametrize("page, is_has_params", PAGES_URLS_PARAMS)
def test_manufactory_user_has_access(
    operator, client, component_factory, page, is_has_params
):
    component = component_factory()
    kwargs = {"pk": component.pk} if is_has_params else {}
    url = reverse(page, kwargs=kwargs)

    client.force_login(operator)
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize("page, is_has_params", PAGES_URLS_PARAMS)
def test_admin_user_has_access(
    admin_client, client, component_factory, page, is_has_params
):
    component = component_factory()
    kwargs = {"pk": component.pk} if is_has_params else {}
    url = reverse(page, kwargs=kwargs)

    response = admin_client.get(url)

    assert response.status_code == 200
