from django.contrib import admin
from .models import Nomenclature, Manufacture, Client, FrameTypeOption, BodyOption


class NomeclatureAdmin(admin.ModelAdmin):
    list_filter = ("status",)


admin.site.register(Nomenclature, NomeclatureAdmin)
admin.site.register(Manufacture)
admin.site.register(Client)

admin.site.register(FrameTypeOption)
admin.site.register(BodyOption)
