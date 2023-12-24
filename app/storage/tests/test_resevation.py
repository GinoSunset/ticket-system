import pytest
from datetime import date

from storage.models import Component
from manufactures.models import Nomenclature, FrameTypeOption
from storage.models import ComponentType
from storage.factories import ComponentFactory, ComponentTypeFactory


def create_components_rs_type(
    inner_component_type: ComponentType | None = None,
) -> ComponentType:
    component = ComponentTypeFactory(name="РЧ", is_internal=True)
    if inner_component_type:
        inner_component_type.parent_component_type = component
        inner_component_type.save()
    return component


@pytest.mark.django_db
def test_has_needs_after_create_manufactory(manufacture_factory, nomenclature_factory):
    create_components_rs_type()
    manuf = manufacture_factory()
    nomenclatures = nomenclature_factory.create_batch(
        3, frame_type=FrameTypeOption.objects.get(name="РЧ"), manufacture=manuf
    )

    assert Component.objects.count() > 0


@pytest.mark.django_db
def test_create_components_with_type_with_sub_component(nomenclature_factory):
    name_sub_component = "Чип РЧ"
    inner_component_type = ComponentTypeFactory(name=name_sub_component)
    component = create_components_rs_type(inner_component_type=inner_component_type)

    nomenclature_factory(frame_type=FrameTypeOption.objects.get(name="РЧ"))

    assert Component.objects.count() == 2
    assert Component.objects.filter(component_type=inner_component_type).exists()


class TestReservation:
    @pytest.mark.django_db
    def test_reserve_already_exists_component_first(self, nomenclature_factory):
        component = ComponentFactory(
            component_type_name="РЧ", is_reserve=False, is_stock=True
        )

        nomenclature = nomenclature_factory(
            frame_type=FrameTypeOption.objects.get(name="РЧ"),
        )

        assert Component.objects.count() == 1
        assert Component.objects.filter(is_reserve=True).count() == 1
        assert Component.objects.filter(is_reserve=False).count() == 0

    @pytest.mark.django_db
    def test_reserve_only_component_with_date_stock_more_that_manufactory_date_shipment(
        self,
        nomenclature_factory,
    ):
        component = ComponentFactory(
            component_type_name="РЧ",
            is_reserve=False,
            date_delivery=date(2021, 1, 1),
            is_stock=False,
        )

        nomenclature = nomenclature_factory(
            frame_type=FrameTypeOption.objects.get(name="РЧ"),
            manufacture__date_shipment=date(2021, 1, 2),
        )

        assert Component.objects.count() == 1
        assert Component.objects.filter(is_reserve=True).first() == component

    @pytest.mark.django_db
    def test_reserve_new_component_when_not_in_stock_and_date_delivery_less_that_manufacture_date_shipment(
        self,
        nomenclature_factory,
    ):
        component = ComponentFactory(
            component_type_name="РЧ",
            is_reserve=False,
            date_delivery=date(2021, 1, 3),
            is_stock=False,
        )

        nomenclature = nomenclature_factory(
            frame_type=FrameTypeOption.objects.get(name="РЧ"),
            manufacture__date_shipment=date(2021, 1, 2),
        )

        assert Component.objects.count() == 2
        assert Component.objects.filter(is_reserve=True).count() == 1
        assert Component.objects.filter(is_reserve=False).first() == component
