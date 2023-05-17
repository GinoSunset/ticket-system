from typing import Any, List, Optional, Tuple, Union
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http.request import HttpRequest
from .models import User, Operator, Customer, Contractor, CustomerProfile
from django.utils.translation import gettext_lazy as _


class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Дополнительная информация",
            {
                "fields": (
                    "avatar",
                    "phone",
                    "role",
                    "token",
                )
            },
        ),
        ("Оповещения", {"fields": ("email_notify", "telegram_id", "telegram_notify")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Дополнительная информация",
            {"fields": ("avatar", "phone", "role", "token")},
        ),
        ("Оповещения", {"fields": ("email_notify", "telegram_id", "telegram_notify")}),
    )
    list_filter = BaseUserAdmin.list_filter + ("role",)

    def get_readonly_fields(self, request, obj=None):
        return list(super().get_readonly_fields(request, obj)) + ["token"]


class ProfileInline(admin.TabularInline):
    model = CustomerProfile
    filter_horizontal = ["linked_operators"]
    extra = 0
    can_delete = False
    show_change_link = True
    verbose_name = _("Профиль")

    def has_add_permission(self, request, obj=None):
        return False


class CustomerAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ("username", "email", "phone")
    search_fields = ("username", "email", "phone")

    def get_readonly_fields(self, request, obj=None):
        return list(super().get_readonly_fields(request, obj)) + ["token"]

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Дополнительная информация", {"fields": ("avatar", "phone", "role", "token")}),
        ("Оповещения", {"fields": ("email_notify", "telegram_notify")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Дополнительная информация", {"fields": ("avatar", "phone", "role", "token")}),
        ("Оповещения", {"fields": ("email_notify", "telegram_notify")}),
    )
    list_filter = BaseUserAdmin.list_filter + ("role",)


admin.site.register(User, UserAdmin)
admin.site.register(Operator, UserAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Contractor, UserAdmin)
