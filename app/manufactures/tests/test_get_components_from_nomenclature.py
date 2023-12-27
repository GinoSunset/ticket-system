import pytest
from manufactures.models import Nomenclature, FrameTypeOption


@pytest.mark.django_db
def test_nomenclature_get_components(nomenclature_factory):
    nomenclature: Nomenclature = nomenclature_factory()
    components = nomenclature.get_components()
    expected_components = [
        f"Плата {nomenclature.frame_type} RX" for _ in range(nomenclature.rx_count)
    ]
    expected_components += [
        f"Плата {nomenclature.frame_type} TX" for _ in range(nomenclature.tx_count)
    ]
    expected_components.append(f"Корпус {nomenclature.frame_type} {nomenclature.body}")
    if nomenclature.mdg:
        expected_components += [
            f"Плата {nomenclature.frame_type} MDG RX"
            for _ in range(nomenclature.rx_count)
        ]
        expected_components += [
            f"Плата {nomenclature.frame_type} MDG TX"
            for _ in range(nomenclature.tx_count)
        ]
    assert components == expected_components


@pytest.mark.django_db
def test_nomenclature_get_components_from_rx(nomenclature_factory):
    nomenclature = nomenclature_factory(rx_count=2)
    components = nomenclature.get_components_from_rx()
    expected_components = [
        f"Плата {nomenclature.frame_type} RX" for _ in range(nomenclature.rx_count)
    ]
    assert components == expected_components


@pytest.mark.django_db
def test_nomenclature_get_components_from_tx(nomenclature_factory):
    nomenclature = nomenclature_factory(tx_count=2)
    components = nomenclature.get_components_from_tx()
    expected_components = [
        f"Плата {nomenclature.frame_type} TX" for _ in range(nomenclature.tx_count)
    ]
    assert components == expected_components


@pytest.mark.django_db
def test_nomenclature_get_components_from_body(nomenclature_factory):
    nomenclature = nomenclature_factory()
    components = nomenclature.get_components_from_body()
    expected_components = [f"Корпус {nomenclature.frame_type} {nomenclature.body}"]
    assert components == expected_components


@pytest.mark.django_db
def test_nomenclature_get_components_from_mdg(nomenclature_factory):
    nomenclature = nomenclature_factory(mdg=True, tx_count=2, rx_count=2)
    components = nomenclature.get_components_from_mdg()
    expected_components = [
        f"Плата {nomenclature.frame_type} MDG RX" for _ in range(nomenclature.rx_count)
    ]
    expected_components += [
        f"Плата {nomenclature.frame_type} MDG TX" for _ in range(nomenclature.tx_count)
    ]
    assert components == expected_components


@pytest.mark.django_db
def test_nomenclature_get_components_from_mdg_rx(nomenclature_factory):
    nomenclature = nomenclature_factory(mdg=True)
    components = nomenclature.get_components_from_mdg_rx()
    expected_components = [
        f"Плата {nomenclature.frame_type} MDG RX" for _ in range(nomenclature.rx_count)
    ]
    assert components == expected_components


@pytest.mark.django_db
def test_nomenclature_get_components_from_mdg_tx(nomenclature_factory):
    nomenclature = nomenclature_factory(mdg=True)
    components = nomenclature.get_components_from_mdg_tx()
    expected_components = [
        f"Плата {nomenclature.frame_type} MDG TX" for _ in range(nomenclature.tx_count)
    ]
    assert components == expected_components


@pytest.mark.django_db
def test_nomenclature_get_components_from_bp(nomenclature_factory):
    nomenclature = nomenclature_factory(
        bp_count=2, frame_type=FrameTypeOption.objects.get(name="АМ")
    )
    components = nomenclature.get_components_from_bp()
    expected_components = ["БП АМ 1А", "БП АМ 1А", "Плата БП АМ", "Плата БП АМ"]
    assert components == expected_components


@pytest.mark.django_db
def test_nomenclature_get_components_from_bp_rs(nomenclature_factory):
    nomenclature = nomenclature_factory(
        bp_count=2, frame_type=FrameTypeOption.objects.get(name="РЧ")
    )
    components = nomenclature.get_components_from_bp()
    expected_components = ["БП РЧ 3.2А", "БП РЧ 3.2А"]
    assert components == expected_components
