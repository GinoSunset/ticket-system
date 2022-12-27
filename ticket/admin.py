from django.contrib import admin

from .models import Ticket, Comment


class TicketAdmin(admin.ModelAdmin):
    pass


class CommentAdmin(admin.ModelAdmin):
    pass


admin.site.register(Ticket, TicketAdmin)
admin.site.register(Comment, CommentAdmin)
