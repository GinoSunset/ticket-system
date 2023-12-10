from django.urls import reverse
import pytest


@pytest.mark.django_db
def test_exist_storage_list_view(client):
    response = client.get(reverse("component-list"))
    assert response.status_code == 200
