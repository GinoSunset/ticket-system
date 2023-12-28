import pytest

from django.urls import reverse
from manufactures.models import Manufacture, Nomenclature
from additionally.models import Dictionary
from manufactures.factories import ManufactureFactory, NomenclatureFactory
from manufactures.forms import NomenclatureForm, ManufactureChangeStatusForm
from manufactures.views import ManufactureUpdateView

# For not process nomenclature in form use this value because in form we have 1 form by default
DO_NOT_PROCESS_NOMENCLATURE = -1


@pytest.mark.django_db
def test_save_auto_save(operator, client):
    status_new = Dictionary.objects.get(code="new_manufacture_task")
    manufacture = ManufactureFactory.create(status=status_new)

    client.force_login(operator)
    status_work = Dictionary.objects.get(code="in_progress")
    res = client.post(
        reverse("manufacture-update", kwargs={"pk": manufacture.pk}),
        data={
            "status": status_work.pk,
            "client": manufacture.client.pk,
            "nomenclature-TOTAL_FORMS": DO_NOT_PROCESS_NOMENCLATURE,
        },
    )
    manuf_after_update = Manufacture.objects.get(pk=manufacture.pk)
    assert manuf_after_update.status != manufacture.status


@pytest.mark.django_db
def test_save_status_if_change_nomenclature(
    operator, nomenclature_factory, manufacture_factory, client
):
    status_new = Dictionary.objects.get(code="new_manufacture_task")

    manufacture = manufacture_factory(status=status_new)
    nomenclature = nomenclature_factory(
        comment="test comment",
        status=Nomenclature.Status.NEW,
        manufacture=manufacture,
    )

    nomenc_form = NomenclatureForm(
        instance=nomenclature, prefix="0", initial={"status": Nomenclature.Status.READY}
    )

    client.force_login(operator)
    res = client.post(
        reverse("manufacture-update", kwargs={"pk": manufacture.pk}),
        data={
            "status": manufacture.status.pk,
            "initial-status": manufacture.status.pk,
            "client": manufacture.client.pk,
            "nomenclature-TOTAL_FORMS": 0,
            **{i.html_name: i.value() for i in nomenc_form},
        },
    )
    manuf_after_update = Manufacture.objects.get(pk=manufacture.pk)
    assert manuf_after_update.status != manufacture.status


@pytest.mark.django_db
def test_save_status_change_and_status_manuf_change(
    client, operator, nomenclature_factory, manufacture_factory
):
    "Status set from form is more important than status from nomenclature"
    manuf = manufacture_factory()
    status_work = Dictionary.objects.get(code="in_progress")
    nomenclature = nomenclature_factory(
        status=Nomenclature.Status.READY, manufacture=manuf
    )
    nomenc_form = NomenclatureForm(instance=nomenclature, prefix="0")

    client.force_login(operator)
    res = client.post(
        reverse("manufacture-update", kwargs={"pk": manuf.pk}),
        data={
            "status": status_work.pk,
            "client": manuf.client.pk,
            "nomenclature-TOTAL_FORMS": 0,
            **{i.html_name: i.value() for i in nomenc_form},
        },
    )
    manuf_after_update = Manufacture.objects.get(pk=manuf.pk)
    assert manuf_after_update.status == status_work


@pytest.mark.django_db
def test_change_status_by_form(
    client, operator, nomenclature_factory, manufacture_factory
):
    manuf = manufacture_factory()
    status_work = Dictionary.objects.get(code="in_progress")
    nomenclature = nomenclature_factory(status=Nomenclature.Status.READY)
    manuf.nomenclatures.add(nomenclature)
    manuf.save()
    client.force_login(operator)
    res = client.post(
        reverse("manufacture-update-status", kwargs={"pk": manuf.pk}),
        data={
            "status": status_work.pk,
        },
    )

    manuf_after_update = Manufacture.objects.get(pk=manuf.pk)
    assert manuf_after_update.status == status_work


@pytest.mark.django_db
def test_change_status_by_form(
    client, operator, nomenclature_factory, manufacture_factory
):
    manuf = manufacture_factory()
    status_work = Dictionary.objects.get(code="in_progress")
    nomenclature = nomenclature_factory(status=Nomenclature.Status.READY)
    manuf.nomenclatures.add(nomenclature)
    manuf.save()
    client.force_login(operator)
    res = client.post(
        reverse("manufacture-update-status", kwargs={"pk": manuf.pk}),
        data={
            "status": status_work.pk,
        },
    )

    manuf_after_update = Manufacture.objects.get(pk=manuf.pk)
    assert manuf_after_update.status == status_work


@pytest.mark.django_db
@pytest.mark.parametrize(
    "statuses, expected_status",
    (
        ([1, 2, 3], "new_manufacture_task"),
        ([2, 3], "in_progress"),
        ([3], "ready"),
        ([3, 3, 3], "ready"),
        ([], "new_manufacture_task"),
        ([4], "shipped"),
    ),
)
def test_min_status_by_nomenclature(
    nomenclature_factory, manufacture_factory, statuses, expected_status
):
    manuf = manufacture_factory()
    for nomenclature_status in statuses:
        manuf.nomenclatures.add(nomenclature_factory(status=nomenclature_status))

    manuf.save()
    view = ManufactureUpdateView()
    view.object = manuf
    assert view.get_status_from_nomenclatures() == Dictionary.objects.get(
        code=expected_status
    )
