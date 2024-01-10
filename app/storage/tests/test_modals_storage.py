import pytest
from storage.models import Component


@pytest.mark.django_db
class TestComponentModel:
    def test_generate_serial_number(self, component_factory, component_type_factory):
        component_type = component_type_factory(name="Test Component Type")
        component_factory(serial_number="AB-123456")
        component_factory(serial_number="CD-789012")

        serial_number = Component.generate_serial_number(component_type)

        assert serial_number.startswith("TE")
        assert len(serial_number) == 11
        assert not Component.objects.filter(serial_number=serial_number).exists()


@pytest.mark.django_db
class TestComponentTypeModel:
    def test_subcomponents_has_count(self, component_type_factory):
        component_type = component_type_factory()
        sub_component_type = component_type_factory()

        sub_component_type.parent_component_type.add(
            component_type, through_defaults={"count_sub_components": 2}
        )
        assert False
