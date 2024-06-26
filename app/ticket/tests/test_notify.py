import pytest

from additionally.models import Dictionary
from django.urls import reverse

from notifications.models import Notification
from ticket.models import Comment, Ticket
from django.core import mail


class TestUpdateTicket:
    @pytest.mark.django_db
    def test_save_comment_update_status(
        self, ticket_factory, client, operator_factory, redis
    ):
        user = operator_factory(first_name="John", last_name="Smit")
        status = Dictionary.objects.get(code="work")
        new_status = Dictionary.objects.get(code="done")
        ticket = ticket_factory(creator=user, status=status)
        user.customers.add(ticket.customer.profile)
        client.force_login(user=user)
        res = client.post(
            reverse("ticket-update", kwargs={"pk": ticket.pk}),
            data={
                "status": new_status.pk,
                "description": ticket.description,
                "customer": ticket.customer.pk,
                "responsible": user.pk,
            },
        )
        comment = Comment.objects.filter(ticket=ticket)
        assert comment.exists()
        assert (
            f"статус изменен c '{status.description}' на '{new_status.description}'"
            in comment.first().text
        )
        assert f"John Smit" in comment.first().text

    @pytest.mark.django_db
    def test_save_comment_update_contractor(
        self,
        ticket_factory,
        contractor_factory,
        client,
        operator_factory,
        monkeypatch_delay_send_email_on_celery,
    ):
        user = operator_factory()
        contractor = contractor_factory()
        status = Dictionary.objects.get(code="work")
        ticket = ticket_factory(creator=user, status=status)
        user.customers.add(ticket.customer.profile)
        client.force_login(user=user)
        client.post(
            reverse("ticket-update", kwargs={"pk": ticket.pk}),
            data={
                "contractor": contractor.pk,
                "description": ticket.description,
                "status": status.pk,
                "customer": ticket.customer.pk,
            },
        )
        comment = Comment.objects.filter(ticket=ticket)
        assert comment.exists()
        assert f"{contractor} назначен(а) исполнителем" in comment.first().text

    @pytest.mark.django_db
    def test_update_status_to_work_create_comment(
        self,
        ticket_factory,
        operator_factory,
        client,
        monkeypatch_delay_send_email_on_celery,
    ):
        user = operator_factory(first_name="John", last_name="Smit")
        status = Dictionary.objects.get(code="new")
        ticket: Ticket = ticket_factory(creator=user, status=status)
        client.force_login(user=user)
        res = client.get(reverse("ticket-to-work", kwargs={"pk": ticket.pk}))
        assert res.status_code == 302
        ticket.refresh_from_db()
        assert ticket.comments.count() == 1
        comment = ticket.comments.first().text
        assert f"статус изменен c " in comment
        assert f"John Smit" in comment

    @pytest.mark.django_db
    def test_update_status_to_done_create_notify_for_customer_with_all_emails(
        self,
        ticket_factory,
        operator_factory,
        customer_factory,
        client,
        monkeypatch_delay_send_email_on_celery,
    ):
        emails = {"cust1@email.com", "cust2@email.com", "cust3@email.com"}
        user = operator_factory(first_name="John", last_name="Smit")
        status = Dictionary.objects.get(code="new")
        customer = customer_factory(email="cust1@email.com")
        ticket: Ticket = ticket_factory(
            creator=user,
            status=status,
            customer=customer,
            _reply_to_emails=",".join(emails),
        )
        client.force_login(user=user)

        res = client.get(reverse("ticket-to-work", kwargs={"pk": ticket.pk}))
        assert res.status_code == 302

        notify = Notification.objects.first()

        assert notify.user == customer
        assert emails == set(mail.outbox[0].to)

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "url", ["ticket-to-work", "ticket-to-done", "ticket-to-cancel"]
    )
    def test_update_status_create_notify_with_all_user_emails_to_copy(
        self,
        ticket_factory,
        operator_factory,
        customer_factory,
        client,
        url,
        monkeypatch_delay_send_email_on_celery,
    ):
        emails = {"cust2@email.com", "cust3@email.com"}
        user = operator_factory(first_name="John", last_name="Smit")
        status = Dictionary.objects.get(code="new")
        customer = customer_factory(email="cust1@email.com")
        customer.refresh_from_db()
        customer.profile.emails = emails
        customer.profile.save()
        ticket: Ticket = ticket_factory(
            creator=user,
            status=status,
            customer=customer,
            shop_id="ЗВ Пушкин Константиновский 112211",
        )
        client.force_login(user=user)

        res = client.get(reverse(url, kwargs={"pk": ticket.pk}))
        assert res.status_code == 302

        notify = Notification.objects.first()

        assert notify.user == customer
        assert emails == set(mail.outbox[0].cc)
        assert f"{ticket.shop_id}" in mail.outbox[0].subject

    @pytest.mark.django_db
    def test_big_file_from_attach_comment_send_as_link(
        self,
        file_5_mb,
        file_1_mb,
        ticket_factory,
        operator_factory,
        customer_factory,
        client,
        monkeypatch_delay_send_email_on_celery,
    ):
        user = operator_factory(first_name="John", last_name="Smit")
        status = Dictionary.objects.get(code="new")
        customer = customer_factory(email="cust1@email.com")
        ticket: Ticket = ticket_factory(
            creator=user,
            status=status,
            customer=customer,
        )
        client.force_login(user=user)
        with open(file_5_mb) as fd:
            comment_data = {"text": "Text1", "is_for_report": True, "files": fd}
            client.post(
                reverse("comment-create", kwargs={"ticket_pk": ticket.pk}),
                data=comment_data,
                format="json",
            )
        with open(file_1_mb) as fd:
            comment_data = {"text": "Text2", "is_for_report": True, "files": fd}
            client.post(
                reverse("comment-create", kwargs={"ticket_pk": ticket.pk}),
                data=comment_data,
                format="json",
            )

        res = client.get(reverse("ticket-to-done", kwargs={"pk": ticket.pk}))
        assert res.status_code == 302

        notify = Notification.objects.first()

        assert len(mail.outbox[0].attachments) == 1, "Only small file in attach"
        assert f"ссылка на прикрепленный файл:" in mail.outbox[0].body
