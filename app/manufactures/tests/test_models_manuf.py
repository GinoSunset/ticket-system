import pytest


@pytest.mark.django_db
def test_create_manuf(manufacture_factory):
    manuf = manufacture_factory()
    assert manuf.id is not None


@pytest.mark.django_db
def test_create_manuf_with_nomenclatures(manufacture_factory, nomenclature_factory):
    batch_ncs = 10
    ncs = nomenclature_factory.create_batch(batch_ncs)
    manuf = manufacture_factory(nomenclatures=ncs)
    assert manuf.id is not None
    assert manuf.nomenclatures.count() == batch_ncs
