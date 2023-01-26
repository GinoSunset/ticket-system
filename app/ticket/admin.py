from django.contrib import admin

from .models import Ticket, Comment


class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "date_create",
        "sap_id",
        "customer",
        "contractor",
        "status",
        "city",
        "id_email_message",
    )
    search_fields = (
        "sap_id",
        "type_ticket__name",
        "customer__username",
        "contractor__username",
    )


class CommentAdmin(admin.ModelAdmin):
    pass


admin.site.register(Ticket, TicketAdmin)
admin.site.register(Comment, CommentAdmin)
