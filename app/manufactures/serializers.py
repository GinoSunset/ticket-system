from django.urls import reverse
from rest_framework import serializers
from .models import Manufacture


class ManufactureSerializer(serializers.ModelSerializer):
    actions = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()

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
            "actions",
        ]

    def get_status_color(self, obj):
        return obj.get_color_status()

    def get_status(self, obj):
        return {"status": obj.status.description, "color": obj.get_color_status()}

    def get_comment(self, obj):
        return {
            "comment": obj.comment,
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
