import pytest
from storage.models import Component, SubComponentTypeRelation
from datetime import datetime


@pytest.mark.django_db
class TestComponentModel:
    def test_generate_serial_number_with_many_word_in_component(
        self, component_factory, component_type_factory
    ):
        component_type = component_type_factory(name="Test Component Type")
        component_factory(serial_number="AB-123456")
        component_factory(serial_number="CD-789012")

        serial_number = Component.generate_serial_number(component_type)

        assert serial_number.startswith("TCT")
        assert len(serial_number) == 12
        assert not Component.objects.filter(serial_number=serial_number).exists()

    def test_generate_serial_number_with_one_word_in_component(
        self, component_factory, component_type_factory
    ):
        component_type = component_type_factory(name="Test")
        component_factory(serial_number="AB-123456")
        component_factory(serial_number="CD-789012")

        serial_number = Component.generate_serial_number(component_type)

        assert serial_number.startswith("TE")
        assert len(serial_number) == 11
        assert not Component.objects.filter(serial_number=serial_number).exists()

    def test_component_has_tags_component_type(self, component, tag_component):
        component.component_type.tags.add(tag_component)
        assert list(component.tags.all()) == [tag_component]


@pytest.mark.django_db
class TestComponentTypeModel:
    def test_subcomponents_has_count(self, component_type_factory):
        component_type = component_type_factory()
        sub_component_type = component_type_factory()

        sub_component_type.parent_component_type.add(
            component_type, through_defaults={"count_sub_components": 2}
        )
        assert (
            SubComponentTypeRelation.objects.get(
                parent_component_type=component_type,
                sub_component_type=sub_component_type,
            ).count_sub_components
            == 2
        )

    def test_component_type_has_tags(
        self, component_type_factory, tag_component, component_factory
    ):
        component_type = component_type_factory()
        component_type.tags.add(tag_component)

        c = component_factory(component_type=component_type)

        c_tag = Component.objects.filter(component_type__tags=tag_component)
        assert c_tag.exists(), "Not found component with tag"


@pytest.mark.parametrize(
    "is_stock, date_delivery, delivery, is_archive ,serial_number, expected",
    [
        (False, None, None, False, None, True),
        (False, None, None, False, "test_serial", False),
        (True, None, None, False, None, False),
        (False, datetime.now(), None, False, None, False),
        (False, None, True, False, None, False),
        (False, None, None, True, None, False),
        (True, None, None, True, None, False),
        (True, datetime.now(), None, True, None, False),
    ],
)
@pytest.mark.django_db
def test_is_phantom_component(
    component_factory,
    delivery_factory,
    is_stock,
    date_delivery,
    delivery,
    is_archive,
    serial_number,
    expected,
):
    if delivery is not None:
        delivery = delivery_factory()
    component = component_factory(
        is_stock=is_stock,
        date_delivery=date_delivery,
        is_archive=is_archive,
        delivery=delivery,
        serial_number=serial_number,
    )

    assert component.is_phantom is expected


@pytest.mark.parametrize(
    "is_stock, date_delivery, delivery, is_archive ,serial_number, expected",
    [
        (False, None, None, False, None, True),
        (False, None, None, False, "test_serial", False),
        (True, None, None, False, None, False),
        (False, datetime.now(), None, False, None, False),
        (False, None, True, False, None, False),
        (False, None, None, True, None, False),
        (True, None, None, True, None, False),
        (True, datetime.now(), None, True, None, False),
    ],
)
@pytest.mark.django_db
def test_phantom_manager_component(
    component_factory,
    delivery_factory,
    is_stock,
    date_delivery,
    delivery,
    is_archive,
    serial_number,
    expected,
):
    if delivery is not None:
        delivery = delivery_factory()
    component_factory(
        is_stock=is_stock,
        date_delivery=date_delivery,
        is_archive=is_archive,
        delivery=delivery,
        serial_number=serial_number,
    )
    c = Component.phantom_components.filter(phantom=True)
    count = 1 if expected else 0
    assert c.count() == count