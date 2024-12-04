from django.urls import reverse
from rest_framework import serializers
from .models import Manufacture


class ManufactureSerializer(serializers.ModelSerializer):
    progress_data = serializers.SerializerMethodField()
    actions = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
    status_color = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

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
            "status_color",
            "comment",
            "progress_data",
            "actions",
        ]

    def get_status_color(self, obj):
        return obj.get_color_status()

    def get_status(self, obj):
        return obj.status.description

    def get_progress_data(self, obj):
        return {
            "total": obj.nomenclatures.count(),
            "value": obj.progress_str_as_list_nomenclatures,
        }

    def get_actions(self, obj):
        return {
            "update_url": reverse("manufacture-update", args=[obj.pk]),
            "print_id": obj.pk,
        }

    def get_client(self, obj):
        return obj.client.name
