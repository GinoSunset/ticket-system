import pytest
from django.urls import reverse
from storage.models import Component, SubComponentTypeRelation, ComponentType

url_com_type_create = reverse("component-type-create")


@pytest.mark.django_db
def test_create_type_component(admin_client, component_type):
    start_count = ComponentType.objects.count()

    data = {
        "name": "Test Component Type",
        "is_internal": False,
        "parents-TOTAL_FORMS": 0,
        "parents-INITIAL_FORMS": "0",
    }

    response = admin_client.post(url_com_type_create, data)

    assert response.status_code == 302
    assert ComponentType.objects.count() - start_count == 1
    assert ComponentType.objects.last().name == "Test Component Type"


@pytest.mark.django_db
def test_create_component_type_with_count(admin_client, component_type_factory):
    parent_component_type = component_type_factory()
    data = {
        "name": "SunComponent",
        "parents-0-parent_component_type": parent_component_type.pk,
        "parents-0-count_sub_components": 2,
        "parents-TOTAL_FORMS": 1,
        "parents-INITIAL_FORMS": "0",
        "parents-MIN_NUM_FORMS": "0",
        "parents-MAX_NUM_FORMS": "1000",
    }
    response = admin_client.post(url_com_type_create, data)
    assert response.status_code == 302

    sub_component = ComponentType.objects.get(name=data["name"])

    relations = SubComponentTypeRelation.objects.get(
        parent_component_type=parent_component_type, sub_component_type=sub_component
    )
    assert relations.count_sub_components == data["parents-0-count_sub_components"]


@pytest.mark.django_db
def test_create_type_component_with_empty_parent_type_not_create_component(
    admin_client, component_type
):
    start_count = ComponentType.objects.count()

    data = {
        "name": "Test Component Type",
        "is_internal": False,
        "parents-TOTAL_FORMS": 1,
        "parents-INITIAL_FORMS": "0",
        "parents-0-count_sub_components": 1,
    }

    response = admin_client.post(url_com_type_create, data)

    assert response.status_code == 200
    assert not ComponentType.objects.filter(name=data["name"]).exists()


@pytest.mark.django_db
def test_create_component_type_with_two_subcomponents(
    admin_client, component_type_factory
):
    parent_component_type = component_type_factory()
    parent_component_type2 = component_type_factory()

    data = {
        "name": "SunComponent",
        "parents-0-parent_component_type": parent_component_type.pk,
        "parents-0-count_sub_components": 2,
        "parents-1-parent_component_type": parent_component_type2.pk,
        "parents-1-count_sub_components": 2,
        "parents-TOTAL_FORMS": 2,
        "parents-INITIAL_FORMS": "0",
    }
    response = admin_client.post(url_com_type_create, data)
    assert response.status_code == 302

    sub_component = ComponentType.objects.get(name=data["name"])

    relations = SubComponentTypeRelation.objects.get(
        parent_component_type=parent_component_type, sub_component_type=sub_component
    )
    assert relations.count_sub_components == data["parents-0-count_sub_components"]


@pytest.mark.django_db
def test_create_component_type_with_two_subcomponents_errors(
    admin_client, component_type_factory
):
    parent_component_type = component_type_factory()
    parent_component_type2 = component_type_factory()

    data = {
        "name": "SunComponent",
        "parents-0-parent_component_type": parent_component_type.pk,
        "parents-0-count_sub_components": 2,
        "parents-1-count_sub_components": 2,
        "parents-TOTAL_FORMS": 2,
        "parents-INITIAL_FORMS": "0",
    }
    response = admin_client.post(url_com_type_create, data)
    assert response.status_code == 200

    assert not response.context_data["parent_forms"][1].is_valid()
