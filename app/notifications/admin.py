from django.contrib import admin
from notifications.models import Notification


class NotificationAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "message", "is_read", "type_notify")
    readonly_fields = ("created_at",)
    list_filter = ("is_read", "type_notify")
    search_fields = ("message", "user__username", "user__email")


admin.site.register(Notification, NotificationAdmin)
