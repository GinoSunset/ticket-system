from rest_framework import serializers
from .models import Manufacture


class ManufactureSerializer(serializers.ModelSerializer):
    data_total = serializers.SerializerMethodField()
    data_value = serializers.SerializerMethodField()

    class Meta:
        model = Manufacture
        fields = [
            "pk",
            "date_create",
            "client",
            "date_shipment",
            "count",
            "branding",
            "status",
            "comment",
            "data_total",
            "data_value",
        ]

    def get_data_total(self, obj):
        return obj.nomenclatures.count()

    def get_data_value(self, obj):
        return obj.progress_str_as_list_nomenclatures
