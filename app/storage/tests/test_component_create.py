import pytest
from storage.forms import ComponentTypeForm, ComponentForm
from storage.models import ComponentType, Component


@pytest.mark.django_db
def test_ComponentTypeForm_valid(component_type):
    form = ComponentTypeForm(
        data={
            "name": "Test Component",
            "is_internal": True,
            "parent_component_type": [component_type.pk],
        }
    )
    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_ComponentTypeForm_invalid():
    form = ComponentTypeForm(data={})
    assert not form.is_valid()


@pytest.mark.django_db
def test_ComponentForm_valid():
    component_type = ComponentType.objects.create(
        name="Test Component", is_internal=True
    )
    form = ComponentForm(
        data={
            "component_type": component_type.pk,
            "is_stock": True,
            "date_delivery": "2022-01-01",
            "is_reserve": False,
            "count": "1",
            "generate_serial_number": True,
        }
    )
    result = form.is_valid()
    assert result


@pytest.mark.django_db
def test_ComponentForm_not_valid_if_undefine_status():
    component_type = ComponentType.objects.create(
        name="Test Component", is_internal=True
    )
    form = ComponentForm(
        data={
            "component_type": component_type.pk,
            "serial_number": "123456",
            "is_stock": False,
            "date_delivery": "",
            "is_reserve": False,
        }
    )
    result = form.is_valid()
    assert not result, "Component has undefined status"
