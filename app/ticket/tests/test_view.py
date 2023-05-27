import pytest
import factory

from django.urls import reverse
from django.db.models import signals
from ticket.models import Comment, Ticket
from users.models import User, Customer, Contractor
from additionally.models import Dictionary
from notifications.models import Notification
from django.core.files.uploadedfile import SimpleUploadedFile
from ticket.models import CommentImage, CommentFile


@pytest.mark.django_db
def test_user_see_ticket_their_customer(
    ticket_factory,
    user_factory,
    client,
    customer_factory,
    monkeypatch_delay_send_email_on_celery,
):
    operator: User = user_factory(role=User.Role.OPERATOR)
    operator = operator.get_role_user()
    their_customer = customer_factory()
    other_customer = customer_factory()
    operator.customers.add(their_customer.profile)
    ticket: Ticket = ticket_factory(customer=their_customer)
    ticket_another = ticket_factory(customer=other_customer)

    client.force_login(user=operator)
    response = client.get(reverse("tickets-list"))

    assert len(response.context_data["ticket_list"]) == 1
    assert response.context_data["ticket_list"][0] == ticket


@pytest.mark.django_db
def test_customer_see_only_self_ticket(
    ticket_factory, user_factory, client, customer_factory
):
    operator = user_factory(role=User.Role.OPERATOR)
    customer: Customer = customer_factory()
    other_customer = customer_factory()
    ticket_another: Ticket = ticket_factory(customer=other_customer, creator=operator)
    ticket: Ticket = ticket_factory(customer=customer, creator=operator)

    client.force_login(user=customer)
    response = client.get(reverse("tickets-list"))

    assert len(response.context_data["ticket_list"]) == 1
    assert response.context_data["ticket_list"][0] == ticket


@pytest.mark.django_db
def test_contractor_see(ticket_factory, user_factory, client, customer_factory):
    operator = user_factory(role=User.Role.OPERATOR)
    customer: Customer = customer_factory()
    contractor: Contractor = user_factory(role=User.Role.CONTRACTOR)
    other_customer = customer_factory()
    ticket_another: Ticket = ticket_factory(customer=other_customer, creator=operator)
    ticket: Ticket = ticket_factory(
        customer=customer, creator=operator, contractor=contractor
    )

    client.force_login(user=contractor)
    response = client.get(reverse("tickets-list"))

    assert len(response.context_data["ticket_list"]) == 1
    assert response.context_data["ticket_list"][0] == ticket


@pytest.mark.django_db
def test_admin_see_all_ticket(
    ticket_factory, user_factory, client, monkeypatch_delay_send_email_on_celery
):
    user1 = user_factory()
    admin_user = user_factory(is_staff=True)
    user_another = user_factory()
    ticket: Ticket = ticket_factory(creator=user1)
    ticket_another = ticket_factory(creator=user_another)
    client.force_login(user=admin_user)
    response = client.get(reverse("tickets-list"))
    assert list(response.context_data["ticket_list"]), list(Ticket.objects.all())


@pytest.mark.django_db
def test_access_page_generate_task_customer(customer_factory, client):
    customer = customer_factory()
    client.force_login(user=customer)
    res = client.get(reverse("tickets-new"))
    assert res.status_code == 200


@pytest.mark.django_db
def test_access_page_generate_task_contractor(user_factory, client):
    contractor = user_factory(role=User.Role.CONTRACTOR)
    client.force_login(user=contractor)
    res = client.get(reverse("tickets-new"))
    assert res.status_code == 200


@pytest.mark.django_db
def test_access_page_update_task_contractor(ticket_factory, user_factory, client):
    contractor = user_factory(role=User.Role.CONTRACTOR)
    ticket = ticket_factory(contractor=contractor)
    client.force_login(user=contractor)
    res = client.get(reverse("ticket-update", kwargs={"pk": ticket.pk}))
    assert res.status_code == 200


@pytest.mark.django_db
def test_access_page_update_task_customer(ticket_factory, customer_factory, client):
    customer = customer_factory()
    ticket = ticket_factory(customer=customer)
    client.force_login(user=customer)
    res = client.get(reverse("ticket-update", kwargs={"pk": ticket.pk}))
    assert res.status_code == 200


@pytest.mark.django_db
def test_access_page_update_task_other(ticket_factory, user_factory, client):
    user = user_factory(role=User.Role.OTHER)
    ticket: Ticket = ticket_factory(creator=user)
    client.force_login(user=user)
    res = client.get(reverse("ticket-update", kwargs={"pk": ticket.pk}))
    assert res.status_code == 200


@pytest.mark.django_db
def test_access_page_create_task_other(user_factory, client):
    user = user_factory(role=User.Role.OTHER)
    client.force_login(user=user)
    res = client.get(reverse("tickets-new"))
    assert res.status_code == 200


@pytest.mark.django_db
def test_customer_save_ticket_has_all_needed_field(customer_factory, client):
    """Исполнитель, Статус, Заказчик"""
    user = customer_factory()
    client.force_login(user=user)
    data = {"description": "bla", "city": "17", "address": "1"}

    res = client.post(reverse("tickets-new"), data=data)

    assert res.status_code == 302

    ticket = Ticket.objects.first()
    assert ticket.creator == user
    assert ticket.customer == user
    assert ticket.status == Dictionary.objects.get(code="work")
    assert ticket.contractor is None


@pytest.mark.django_db
def test_update_ticket_has_set_status_on_html_select(
    ticket_factory, operator_factory, client
):
    user = operator_factory()
    status = Dictionary.objects.get(code="consideration")
    ticket = ticket_factory(creator=user, status=status)
    client.force_login(user=user)
    res = client.get(reverse("ticket-update", kwargs={"pk": ticket.pk}))
    assert res.status_code == 200
    widget = res.context_data["form"].fields["status"].widget
    assert (
        f'<option value="{status.pk}" selected>{status.description}</option>'
        in res.content.decode()
    )


@pytest.mark.django_db
def test_delete_comment_image_by_operator(
    ticket_factory,
    operator_factory,
    client,
    monkeypatch_delay_send_email_on_celery,
    comment_factory,
):
    user = operator_factory()
    comment = comment_factory(author=user)
    image = comment.images.create(image=SimpleUploadedFile("test.jpg", b"test"))
    client.force_login(user=user)
    res = client.post(reverse("delete-comment-image", kwargs={"pk": image.pk}))
    assert res.status_code == 302
    assert not CommentImage.objects.filter(pk=image.pk).exists()


@pytest.mark.django_db
def test_delete_comment_file_by_operator(
    operator_factory,
    client,
    monkeypatch_delay_send_email_on_celery,
    comment_factory,
):
    user = operator_factory()
    comment = comment_factory(author=user)
    file = comment.files.create(file=SimpleUploadedFile("test.pdf", b"pdf"))
    client.force_login(user=user)
    res = client.post(reverse("delete-comment-file", kwargs={"pk": file.pk}))
    assert res.status_code == 302
    assert not CommentFile.objects.filter(pk=file.pk).exists()


@pytest.mark.django_db
def test_update_comment(
    comment_factory, monkeypatch_delay_send_email_on_celery, client, operator_factory
):
    user = operator_factory()
    comment = comment_factory(author=user, text="bla")
    client.force_login(user=user)
    res = client.post(
        reverse(
            "comment-update", kwargs={"ticket_pk": comment.ticket.pk, "pk": comment.pk}
        ),
        data={"text": "new_text"},
    )
    assert res.status_code == 302
    comment.refresh_from_db()
    assert comment.text == "new_text"


class TestUpdateTicketPage:
    @pytest.mark.django_db
    def test_update_ticket_by_customer_has_not_form_in_context(
        self, ticket_factory, customer_factory, client
    ):
        user = customer_factory()
        ticket = ticket_factory(customer=user)
        client.force_login(user=user)
        res = client.get(reverse("ticket-update", kwargs={"pk": ticket.pk}))
        assert res.status_code == 200
        assert "form" not in res.context_data

    @pytest.mark.django_db
    def test_update_ticket_by_operator_has_form_in_context(
        self, ticket_factory, operator_factory, client, customer_factory
    ):
        operator = operator_factory()
        customer = customer_factory()
        ticket = ticket_factory(customer=customer)
        operator.customers.add(ticket.customer.profile)
        client.force_login(user=operator)
        res = client.get(reverse("ticket-update", kwargs={"pk": ticket.pk}))
        assert res.status_code == 200
        assert "form" in res.context_data

    @pytest.mark.django_db
    def test_update_status_to_work(
        self,
        ticket_factory,
        operator_factory,
        client,
        monkeypatch_delay_send_email_on_celery,
    ):
        user = operator_factory()
        status = Dictionary.objects.get(code="new")
        ticket: Ticket = ticket_factory(creator=user, status=status)
        client.force_login(user=user)
        res = client.get(reverse("ticket-to-work", kwargs={"pk": ticket.pk}))
        assert res.status_code == 302
        ticket.refresh_from_db()
        assert ticket.status == Dictionary.objects.get(code="work")
        assert ticket.responsible == user

    @pytest.mark.django_db
    def test_update_status_to_cancel(
        self,
        ticket_factory,
        operator_factory,
        client,
        monkeypatch_delay_send_email_on_celery,
    ):
        user = operator_factory()
        status = Dictionary.objects.get(code="new")
        ticket: Ticket = ticket_factory(creator=user, status=status)
        client.force_login(user=user)

        res = client.get(reverse("ticket-to-cancel", kwargs={"pk": ticket.pk}))
        assert res.status_code == 302
        ticket.refresh_from_db()
        assert ticket.status == Dictionary.objects.get(code="cancel")


class TestCommentViews:
    @pytest.mark.django_db
    def test_create_comment_with_flag_is_for_report(
        self,
        ticket_factory,
        operator_factory,
        client,
        monkeypatch_delay_send_email_on_celery,
    ):
        user = operator_factory()
        ticket = ticket_factory(creator=user)
        client.force_login(user=user)
        res = client.post(
            reverse("comment-create", kwargs={"ticket_pk": ticket.pk}),
            data={"text": "bla", "is_for_report": True},
        )
        assert res.status_code == 302
        comment = Comment.objects.first()
        assert comment.is_for_report


class TestUpdateContractorViewPage:
    @factory.django.mute_signals(signals.post_save)
    @pytest.mark.django_db
    def test_update_contractor(
        self, contractor_factory, operator_factory, client, ticket_factory
    ):
        ticket = ticket_factory()
        user = operator_factory()
        contractor = contractor_factory()
        client.force_login(user=user)
        res = client.post(
            reverse("update-contractor", kwargs={"pk": ticket.pk}),
            data={"contractor": contractor.pk},
        )
        assert res.status_code == 200
        ticket.refresh_from_db()
        assert ticket.contractor == contractor

    @factory.django.mute_signals(signals.post_save)
    @pytest.mark.django_db
    def test_failed_update_contractor_return_400(
        self, operator_factory, client, ticket_factory
    ):
        ticket = ticket_factory()
        user = operator_factory()
        client.force_login(user=user)
        res = client.post(
            reverse("update-contractor", kwargs={"pk": ticket.pk}),
            data={"contractor": 1000000},
        )
        assert res.status_code == 400

    @pytest.mark.django_db
    @factory.django.mute_signals(signals.post_save)
    def test_create_notify_after_save_new_contractor(
        self, ticket_factory, contractor_factory, operator_factory, client
    ):
        ticket = ticket_factory()
        user = operator_factory()
        contractor = contractor_factory()
        client.force_login(user=user)
        res = client.post(
            reverse("update-contractor", kwargs={"pk": ticket.pk}),
            data={"contractor": contractor.pk},
        )
        assert res.status_code == 200
        assert Notification.objects.filter(
            ticket=ticket, type_notify=Notification.TypeNotification.SET_CONTRACTOR
        ).exists()
