from django.contrib import admin

from .models import User, Operator, Customer, Contractor, CustomerProfile

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    pass


class ProfileInline(admin.TabularInline):
    model = CustomerProfile
    filter_horizontal = ["linked_operators"]


class CustomerAdmin(admin.ModelAdmin):
    inlines = (ProfileInline,)


admin.site.register(User, UserAdmin)
admin.site.register(Operator, UserAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Contractor, UserAdmin)
