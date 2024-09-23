import pytest
import factory

from django.db.models import signals
from django.urls import reverse
from manufactures.models import Manufacture, Nomenclature
from additionally.models import Dictionary
from manufactures.factories import ManufactureFactory, NomenclatureFactory
from manufactures.forms import NomenclatureForm, ManufactureChangeStatusForm
from manufactures.views import ManufactureUpdateView, ManufactureStatusUpdateView
from ticket.signals import post_save as post_save_ticket

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


@factory.django.mute_signals(signals.post_save)
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
        instance=nomenclature,
        prefix="0",
        initial={"status": Nomenclature.Status.READY},
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


@factory.django.mute_signals(signals.post_save)
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


@factory.django.mute_signals(signals.post_save)
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


@factory.django.mute_signals(signals.post_save)
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


@factory.django.mute_signals(signals.post_save)
@pytest.mark.django_db
@pytest.mark.parametrize(
    "statuses",
    (
        ([1]),
        ([1, 4, 2]),
        ([1, 4]),
        ([1, 4, 5]),
    ),
)
def test_update_status_to_nomenclature_by_manufacture_ready(
    client, manufacture_factory, nomenclature_factory, operator, statuses
):
    manuf = manufacture_factory()
    for nomenclature_status in statuses:
        manuf.nomenclatures.add(nomenclature_factory(status=nomenclature_status))
    manuf.save()

    client.force_login(operator)
    client.post(
        reverse("manufacture-update-status", kwargs={"pk": manuf.pk}),
        data={
            "status": Dictionary.objects.get(code="ready").pk,
        },
    )

    expected_status = []
    for nomenclature_status in statuses:
        if nomenclature_status <= Nomenclature.Status.READY:
            expected_status.append(Nomenclature.Status.READY.value)
        else:
            expected_status.append(nomenclature_status)

    assert (
        list(
            manuf.nomenclatures.all()
            .order_by("date_create")
            .values_list("status", flat=True)
        )
        == expected_status
    )


@factory.django.mute_signals(signals.post_save)
@pytest.mark.django_db
@pytest.mark.parametrize(
    "statuses",
    (
        ([1]),
        ([1, 4, 2]),
        ([1, 4]),
        ([1, 4, 5]),
    ),
)
def test_update_status_to_nomenclature_by_manufacture_canceled(
    client, manufacture_factory, nomenclature_factory, operator, statuses
):
    manuf = manufacture_factory()
    for nomenclature_status in statuses:
        manuf.nomenclatures.add(nomenclature_factory(status=nomenclature_status))
    manuf.save()

    client.force_login(operator)
    client.post(
        reverse("manufacture-update-status", kwargs={"pk": manuf.pk}),
        data={
            "status": Dictionary.objects.get(code="canceled").pk,
        },
    )

    expected_status = []
    for nomenclature_status in statuses:
        if nomenclature_status <= Nomenclature.Status.CANCELED:
            expected_status.append(Nomenclature.Status.CANCELED.value)
        else:
            expected_status.append(nomenclature_status)

    assert (
        list(
            manuf.nomenclatures.all()
            .order_by("date_create")
            .values_list("status", flat=True)
        )
        == expected_status
    )


@factory.django.mute_signals(post_save_ticket)
@pytest.mark.django_db
def test_create_manufacture_with_ticket(
    ticket_factory,
    customer_profile_factory,
    operator_client,
    redis,
):
    ticket = ticket_factory()
    customer_profile_factory(user=ticket.customer)
    url = reverse("manufactures-create") + f"?ticket={ticket.pk}"
    res = operator_client.get(url)
    title_page = res.context_data.get("name_page")
    form = res.context_data.get("form")
    assert (
        title_page
        == f"Создание задачи на производство для задачи <a href='{reverse('ticket-update', args=str(ticket.pk))}' >#{ticket.pk}</a>"
    ), "Имя страницы не правильное "

    # assert form.initial.get("client") == ticket.customer


@factory.django.mute_signals(post_save_ticket)
@pytest.mark.django_db
def test_create_system_comment_for_ticket_when_create_manufactory(
    ticket_factory, customer_profile_factory, operator_client, manufacture_client
):
    """
    Проверяет, создается ли системный комментарий после создания задачи
    на производство из под заявки
    """

    ticket = ticket_factory()
    customer_profile_factory(user=ticket.customer)
    url = reverse("manufactures-create") + f"?ticket={ticket.pk}"

    status_work = Dictionary.objects.get(code="in_progress")
    res = operator_client.post(
        url,
        data={
            "status": status_work.pk,
            "client": manufacture_client.pk,
            "nomenclature-TOTAL_FORMS": DO_NOT_PROCESS_NOMENCLATURE,
        },
    )
    assert ticket.comments.count() == 1, "Comment not created"


@factory.django.mute_signals(post_save_ticket)
@pytest.mark.django_db
def test_redirect_to_ticket_for_ticket_when_create_manufactory_with_ticket(
    ticket_factory,
    customer_profile_factory,
    operator_client,
    manufacture_client,
):
    """
    Проверяет, происходиит лии рилдерект на страницу с описанием задачи
    после создания заявки
    """

    ticket = ticket_factory()
    customer_profile_factory(user=ticket.customer)
    url = reverse("manufactures-create") + f"?ticket={ticket.pk}"

    status_work = Dictionary.objects.get(code="in_progress")
    res = operator_client.post(
        url,
        data={
            "status": status_work.pk,
            "client": manufacture_client.pk,
            "nomenclature-TOTAL_FORMS": DO_NOT_PROCESS_NOMENCLATURE,
        },
    )
    assert res.status_code == 302
    assert res.url == reverse("ticket-update", kwargs={"pk": ticket.pk})


@factory.django.mute_signals(post_save_ticket)
@pytest.mark.django_db
def test_redirect_to_ticket_for_ticket_when_update_manufactory_with_ticket(
    ticket_factory,
    customer_profile_factory,
    operator_client,
    manufacture_client,
    manufacture_factory,
):
    """
    Проверяет, происходиит лии рилдерект на страницу с описанием задачи
    после обновления заявки
    """

    ticket = ticket_factory()
    customer_profile_factory(user=ticket.customer)
    manuf = manufacture_factory(ticket=ticket)
    url = (
        reverse("manufacture-update", kwargs={"pk": manuf.pk}) + f"?ticket={ticket.pk}"
    )

    status_work = Dictionary.objects.get(code="in_progress")
    res = operator_client.post(
        url,
        data={
            "status": status_work.pk,
            "client": manufacture_client.pk,
            "nomenclature-TOTAL_FORMS": DO_NOT_PROCESS_NOMENCLATURE,
        },
    )
    assert res.status_code == 302
    assert res.url == reverse("ticket-update", kwargs={"pk": ticket.pk})


@factory.django.mute_signals(post_save_ticket)
@pytest.mark.django_db
def test_set_ticket_in_form_for_manufacture_with_ticket(
    ticket_factory,
    customer_profile_factory,
    operator_client,
    manufacture_client,
    manufacture_factory,
):
    """
    Проверяет, что на странице обновления производства установлен по умолчанию
    изначальный тикет
    """

    ticket = ticket_factory()
    customer_profile_factory(user=ticket.customer)
    manuf = manufacture_factory(ticket=ticket)
    url = reverse("manufacture-update", kwargs={"pk": manuf.pk})

    res = operator_client.get(url)
    ticket_from_form = res.context_data.get("form")["ticket"].value()
    assert ticket_from_form == manuf.ticket.pk
