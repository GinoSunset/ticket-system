from django.contrib import admin

from .models import Dictionary, DictionaryType, Click


class DictionaryAdmin(admin.ModelAdmin):
    search_fields = ("code", "description")
    list_display = ("code", "type_dict", "description")


class DictionaryTypeAdmin(admin.ModelAdmin):
    search_fields = ("code", "description")
    list_display = ("code", "description")


admin.site.register(Dictionary, DictionaryAdmin)
admin.site.register(DictionaryType, DictionaryTypeAdmin)
