import pytest
from django.db.models import signals
import factory

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
    expected_components += [
        f"Корпус {nomenclature.frame_type} {nomenclature.body}"
        for _ in range(nomenclature.rx_count + nomenclature.tx_count)
    ]
    if nomenclature.mdg:
        expected_components += [
            f"Плата {nomenclature.frame_type} MDG RX"
            for _ in range(nomenclature.rx_count)
        ]
        expected_components += [
            f"Плата {nomenclature.frame_type} MDG TX"
            for _ in range(nomenclature.tx_count)
        ]
    expected_components += ["БП АМ 1А", "Плата БП АМ"]
    assert sorted(components) == sorted(expected_components)


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
@pytest.mark.parametrize(
    "rx_count, tx_count, expected_count", ([1, 1, 2], [2, 2, 4], [1, 2, 3], [2, 1, 3])
)
def test_nomenclature_get_components_from_body(
    nomenclature_factory, rx_count, tx_count, expected_count
):
    nomenclature = nomenclature_factory(rx_count=rx_count, tx_count=tx_count)
    components = nomenclature.get_components_from_body()
    expected_components = [
        f"Корпус {nomenclature.frame_type} {nomenclature.body}"
        for _ in range(expected_count)
    ]
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


@pytest.mark.django_db
@pytest.mark.parametrize(
    "comment, expected_components, count",
    [
        ("необходимо {деатоватор 4 шт}", ["деатоватор"], 4),
        (
            "необходимо {деатоватор 4 шт} {преобразователь 2 шт}",
            ["деатоватор", "преобразователь"],
            6,
        ),
        (
            "необходимо {деатоватор 4 шт} {преобразователь 2 шт} {преобразователь 2 шт}",
            ["деатоватор", "преобразователь"],
            8,
        ),
    ],
)
@factory.django.mute_signals(signals.post_save)
def test_get_components_from_comment(
    nomenclature_factory, comment, expected_components, count
):
    nomenclature = nomenclature_factory(comment=comment)
    components = nomenclature.get_components_from_comment()

    assert len(components) == count
    for component in expected_components:
        assert component in components
