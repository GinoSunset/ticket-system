from django.contrib import admin

from .models import Ticket, Comment, CommentFile, CommentImage


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
        "date_update",
        "date_create",
    )
    readonly_fields = ("date_update", "date_create")
    search_fields = (
        "pk",
        "sap_id",
        "type_ticket__description",
        "customer__username",
        "contractor__username",
        "status__description",
    )


class CommentAdmin(admin.ModelAdmin):
    pass


class CommentFileAdmin(admin.ModelAdmin):
    pass


class CommentImageAdmin(admin.ModelAdmin):
    pass


admin.site.register(Ticket, TicketAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(CommentFile, CommentFileAdmin)
admin.site.register(CommentImage, CommentImageAdmin)
