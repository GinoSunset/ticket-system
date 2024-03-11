import pytest
import pytest

from manufactures.models import Manufacture, Nomenclature
from additionally.models import Dictionary, DictionaryType
from storage.models import Component, ComponentType


@pytest.mark.django_db
def test_all_components_has_status_archive_after_status_to_shipment(
    nomenclature_factory, monkeypatch_delay_reserve_component_celery
):
    nomenclature = nomenclature_factory()
    nomenclature.status = nomenclature.Status.SHIPPED

    nomenclature.save()

    components = Component.objects.filter(nomenclature=nomenclature)
    assert all([component.is_archive for component in components])


@pytest.mark.django_db
def test_change_update_composenent_after_up_count_nomenclature_components(
    nomenclature_factory, monkeypatch_delay_reserve_component_celery
):
    nomenclature = nomenclature_factory(rx_count=1)
    componet_typeAM_RX = ComponentType.objects.get(pk=1)
    assert (
        Component.objects.filter(
            nomenclature=nomenclature, component_type=componet_typeAM_RX
        ).count()
        == 1
    )

    nomenclature.rx_count = 2
    nomenclature.save()

    assert (
        Component.objects.filter(
            nomenclature=nomenclature, component_type=componet_typeAM_RX
        ).count()
        == 2
    )


@pytest.mark.django_db
def test_phantom_component_remove_after_cancel(
    nomenclature_factory, monkeypatch_delay_reserve_component_celery
):
    nomenclature: Nomenclature = nomenclature_factory()
    components = Component.objects.filter(nomenclature=nomenclature)
    assert all([component.is_phantom for component in components])

    nomenclature.status = nomenclature.Status.CANCELED
    nomenclature.save()

    assert Component.objects.filter(nomenclature=nomenclature).exists() is False


@pytest.mark.django_db
def test_phantom_component_remove_after_delete(
    nomenclature_factory, monkeypatch_delay_reserve_component_celery
):
    nomenclature: Nomenclature = nomenclature_factory()
    components_id = list(
        Component.objects.filter(nomenclature=nomenclature).values_list("pk", flat=True)
    )

    nomenclature.delete()

    assert Component.objects.filter(id__in=components_id).exists() is False


@pytest.mark.django_db
def test_component_move_remove_reservation_after_cancel(
    nomenclature_factory, monkeypatch_delay_reserve_component_celery
):
    assert False


@pytest.mark.django_db
def test_component_remove_reservation_after_delete(
    nomenclature_factory, monkeypatch_delay_reserve_component_celery
):
    assert False


@pytest.mark.django_db
def test_rebalanced_reservation_after_cancel_nomenclature(
    nomenclature_factory, monkeypatch_delay_reserve_component_celery
):
    assert False


@pytest.mark.django_db
def test_rebalanced_reservation_after_remove_nomenclature(
    nomenclature_factory, monkeypatch_delay_reserve_component_celery
):
    assert False
