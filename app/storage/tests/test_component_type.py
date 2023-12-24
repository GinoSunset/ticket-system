import pytest
from django.urls import reverse
from storage.models import ComponentType
from storage.forms import ComponentTypeForm
from storage.models import Component


@pytest.mark.django_db
def test_create_type_component(client, component_type):
    url = reverse("component-type-create")
    data = {
        "name": "Test Component Type",
        "is_internal": False,
        "parent_component_type": [component_type.pk],
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert ComponentType.objects.count() == 2
    assert ComponentType.objects.last().name == "Test Component Type"


@pytest.mark.django_db
def test_create_type_component_with_sub_component(client):
    component = ComponentType.objects.create(
        name="Test Component Type", is_internal=False
    )
    url = reverse("component-type-create")
    data = {
        "name": "Test Component Type 2",
        "is_internal": False,
        "parent_component_type": component.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert ComponentType.objects.count() == 2
    assert (
        ComponentType.objects.get(name="Test Component Type 2")
        .parent_component_type.get()
        .pk
        == component.pk
    )
