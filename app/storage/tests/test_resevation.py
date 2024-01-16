import pytest
from datetime import date, datetime

from storage.models import Component
from manufactures.models import Nomenclature, FrameTypeOption
from storage.models import ComponentType
from storage.factories import ComponentFactory, ComponentTypeFactory
from storage.reserve import unreserve_components


def get_components_rs_type(
    inner_component_type: ComponentType | None = None,
) -> ComponentType:
    component, _ = ComponentType.objects.get_or_create(name="Плата РЧ RX")
    if inner_component_type:
        inner_component_type.parent_component_type.add(component)
        inner_component_type.save()
    return component


@pytest.mark.django_db
def test_has_needs_after_create_manufactory(manufacture_factory, nomenclature_factory):
    get_components_rs_type()
    manuf = manufacture_factory()
    nomenclatures = nomenclature_factory.create_batch(
        3, frame_type=FrameTypeOption.objects.get(name="РЧ"), manufacture=manuf
    )

    assert Component.objects.count() > 0


@pytest.mark.django_db
def test_create_components_with_type_with_sub_component(
    nomenclature_factory, component_type_factory
):
    name_sub_component = "Чип РЧ"
    inner_component_type = component_type_factory(name=name_sub_component)
    component = get_components_rs_type(inner_component_type=inner_component_type)

    nomenclature_factory(frame_type=FrameTypeOption.objects.get(name="РЧ"))

    assert Component.objects.filter(component_type=inner_component_type).exists()


class TestReservation:
    @pytest.mark.django_db
    def test_reserve_already_exists_component_first(self, nomenclature_factory):
        ComponentType.objects.all().delete()
        component = ComponentFactory(
            component_type=get_components_rs_type(), is_reserve=False, is_stock=True
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
        ComponentType.objects.all().delete()

        component = ComponentFactory(
            component_type_name="Плата РЧ RX",
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
        ComponentType.objects.all().delete()

        component = ComponentFactory(
            component_type_name="Плата РЧ RX",
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


@pytest.mark.django_db
class TestUnreserveComponents:
    def test_unreserve_components(self, nomenclature_factory, component_factory):
        nomenclature = nomenclature_factory()
        component1 = component_factory(
            nomenclature=nomenclature,
            is_stock=False,
            is_reserve=True,
            date_delivery=None,
        )
        component2 = component_factory(
            nomenclature=nomenclature,
            is_stock=False,
            is_reserve=True,
            date_delivery=datetime.now(),
        )
        component3 = component_factory(
            nomenclature=nomenclature,
            is_stock=True,
            is_reserve=True,
            date_delivery=None,
        )

        unreserve_components(nomenclature)
        component2.refresh_from_db()
        component3.refresh_from_db()

        assert Component.objects.filter(pk=component1.pk).exists() is False
        assert component2.is_reserve is False
        assert component3.is_reserve is False

        assert Component.objects.filter(nomenclature=nomenclature).count() == 0


@pytest.mark.django_db
class TestSignalReservation:
    def test_signal_after_update_component(self, nomenclature_factory):
        nomenclature = nomenclature_factory()
        component_bp = Component.objects.filter(
            nomenclature=nomenclature, component_type__name__contains="БП АМ"
        )
        count_before_add = component_bp.count()

        nomenclature.bp_count *= 2
        nomenclature.save()

        components = Component.objects.filter(
            nomenclature=nomenclature, component_type__name__contains="БП АМ"
        )
        assert components.count() == count_before_add * 2

    def test_reduce_count_components_after_update_nomenclature(
        self, nomenclature_factory, component_factory
    ):
        """
        Создается 2 компонента БП АМ 1А
        Создается номенклатура с 2 компонентами БП АМ 1А
        После обновления номенклатуры кол-во компонентов БП АМ 1А должно уменьшиться на 1
        """
        Component.objects.all().delete()
        component_type_bp = ComponentType.objects.filter(name__contains="БП АМ 1А")
        for component_type in component_type_bp:
            c1 = component_factory(
                component_type=component_type, is_stock=True, nomenclature=None
            )
            c2 = component_factory(
                component_type=component_type, is_stock=True, nomenclature=None
            )

        nomenclature = nomenclature_factory(bp_count=2)

        components_bp_before_update = Component.objects.filter(
            component_type__name__contains="БП АМ 1А",
            is_reserve=True,
            nomenclature=nomenclature,
        )

        count_before_update = components_bp_before_update.count()
        pks_before_update = [component.pk for component in components_bp_before_update]
        print(pks_before_update)

        nomenclature.bp_count = 1
        nomenclature.save()

        assert (
            Component.objects.filter(
                component_type__name__contains="БП АМ 1А",
                is_reserve=True,
                nomenclature=nomenclature,
            ).count()
            == count_before_update / 2
        )

        components_after_update = Component.objects.filter(pk__in=pks_before_update)

        assert components_after_update.filter(pk=c1.pk).exists()
        assert Component.objects.filter(pk=c2.pk).exists()
        assert (
            Component.objects.filter(
                nomenclature=nomenclature, component_type__name__contains="БП АМ 1А"
            ).count()
            == 1
        )


@pytest.mark.django_db
def test_reservation_component_from_comment(
    nomenclature_factory, component_type_factory
):
    ct = component_type_factory(name="деатоватор")
    comment = "необходимо {деатоватор  4 шт}"
    nomenclature = nomenclature_factory(comment=comment)

    assert Component.objects.filter(component_type=ct).count() == 4
    assert Component.objects.filter(component_type=ct, is_reserve=True).count() == 4
