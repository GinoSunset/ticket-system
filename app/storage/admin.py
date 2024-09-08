from django.contrib import admin
from .models import (
    Component,
    ComponentType,
    Alias,
    SubComponentTypeRelation,
    Delivery,
    TagComponent,
    Invoice,
)


class AliasInline(admin.TabularInline):
    model = Alias

class InvoiceAdmin(admin.ModelAdmin):
    pass


class InvoiceInLine(admin.TabularInline):
    model = Invoice


class ComponentTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "is_internal", "display_tags")
    list_filter = ("parent_component_type", "is_internal", "tags")
    search_fields = ("name",)
    filter_horizontal = ("tags",)
    inlines = [AliasInline]

    def display_tags(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())

    display_tags.short_description = "Теги"


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

    def get_queryset(self, request):
        return Component.objects.get_queryset()


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
    inlines = [InvoiceInLine]


class TagComponentAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


admin.site.register(Component, ComponentAdmin)
admin.site.register(ComponentType, ComponentTypeAdmin)
admin.site.register(Alias, AliasAdmin)
admin.site.register(SubComponentTypeRelation, SubComponentTypeRelationAdmin)
admin.site.register(Delivery, DeliveryAdmin)
admin.site.register(TagComponent, TagComponentAdmin)
admin.site.register(Invoice, InvoiceAdmin)
