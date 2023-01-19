from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Operator, Customer, Contractor, CustomerProfile
from django.utils.translation import gettext_lazy as _

# Register your models here.
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Дополнительная информация", {"fields": ("avatar", "phone", "role")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Дополнительная информация", {"fields": ("avatar", "phone", "role")}),
    )
    list_filter = BaseUserAdmin.list_filter + ("role",)


class ProfileInline(admin.TabularInline):
    model = CustomerProfile
    filter_horizontal = ["linked_operators"]


class CustomerAdmin(admin.ModelAdmin):
    inlines = (ProfileInline,)
    list_display = ("username", "email", "phone")
    search_fields = ("username", "email", "phone")


admin.site.register(User, UserAdmin)
admin.site.register(Operator, UserAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Contractor, UserAdmin)
