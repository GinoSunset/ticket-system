from django.urls import reverse
from django.utils.html import format_html
from rest_framework import serializers
from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    type_ticket = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    responsible = serializers.SerializerMethodField()
    contractor = serializers.SerializerMethodField()
    detail_ticket_link = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            "id",
            "date_create",
            "sap_id",
            "type_ticket",
            "customer",
            "responsible",
            "contractor",
            "planned_execution_date",
            "status",
            "city",
            "shop_id",
            "detail_ticket_link",
        ]

    def get_customer(self, ticket: Ticket):
        customer = ticket.customer.get_role_user()
        if hasattr(customer, "short_str"):
            return customer.short_str()
        return ""

    def get_responsible(self, ticket: Ticket):
        if not ticket.responsible:
            return ""
        return str(ticket.responsible)

    def get_contractor(self, ticket: Ticket):
        if not ticket.contractor:
            return ""
        return str(ticket.contractor)

    def get_type_ticket(self, ticket: Ticket):
        return str(ticket.type_ticket)

    def get_status(self, ticket: Ticket):
        # <td data-label="status" class={{ ticket.get_colored_status_if_dup_shop }}>
        if ticket.status:
            if ticket.get_colored_status_if_dup_shop():
                return f'<div class="ui {ticket.get_color_status()} label">{ticket.status}!</div>'
            return f'<div class="ui {ticket.get_color_status()} label">{ticket.status}</div>'
        return ""

    def get_detail_ticket_link(self, ticket: Ticket):
        link = reverse("ticket-update", kwargs={"pk": ticket.pk})
        return format_html(
            f'<a class="ui button info" target="_blank" href={link}>Просмотр</a>'
        )
