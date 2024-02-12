from django.contrib import admin
from .models import Component, ComponentType, Alias, SubComponentTypeRelation, Delivery


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
        "is_archive",
        "nomenclature",
        "delivery",
    )
    list_filter = ("component_type", "is_stock", "is_reserve", "is_archive", "delivery")
    list_editable = ("is_stock", "is_reserve")
    search_fields = (
        "component_type__name",
        "serial_number",
        "nomenclature__manufacture__pk",
        "delivery__pk",
    )


class SubComponentTypeRelationAdmin(admin.ModelAdmin):
    list_display = (
        "parent_component_type",
        "sub_component_type",
        "count_sub_components",
    )
    list_filter = (
        "parent_component_type",
        "sub_component_type",
    )
    list_editable = ("count_sub_components",)


class DeliveryAdmin(admin.ModelAdmin):
    list_display = ("id", "date_create", "date_delivery", "status")
    list_editable = ("status", "date_delivery")
    list_filter = ("status", "date_delivery")


admin.site.register(Component, ComponentAdmin)
admin.site.register(ComponentType, ComponentTypeAdmin)
admin.site.register(Alias, AliasAdmin)
admin.site.register(SubComponentTypeRelation, SubComponentTypeRelationAdmin)
admin.site.register(Delivery, DeliveryAdmin)
