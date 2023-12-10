import pytest
from django.urls import reverse
from storage.models import ComponentType
from storage.forms import ComponentTypeForm


@pytest.mark.django_db
def test_create_component(client):
    url = reverse("component_create")
    response = client.post(url, data)
    assert response.status_code == 302
    assert Component.objects.count() == 1
    assert Component.objects.get().name == "Test Component"
