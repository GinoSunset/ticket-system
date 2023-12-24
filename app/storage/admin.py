from django.contrib import admin
from .models import Component, ComponentType, Alias


class AliasInline(admin.TabularInline):
    model = Alias


class ComponentTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "is_internal")
    list_filter = ("parent_component_type", "is_internal")
    search_fields = ("name",)
    inlines = [AliasInline]


class AliasAdmin(admin.ModelAdmin):
    list_display = ("name", "component_type")
    list_filter = ("component_type",)
    search_fields = ("name",)


class ComponentAdmin(admin.ModelAdmin):
    list_display = (
        "component_type",
        "serial_number",
        "is_stock",
        "date_delivery",
        "is_reserve",
        "nomenclature",
    )
    list_filter = ("component_type", "is_stock", "is_reserve")
    list_editable = ("is_stock", "is_reserve")
    search_fields = (
        "component_type__name",
        "serial_number",
    )


admin.site.register(Component, ComponentAdmin)
admin.site.register(ComponentType, ComponentTypeAdmin)
admin.site.register(Alias, AliasAdmin)
