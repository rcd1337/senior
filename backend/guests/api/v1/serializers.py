from rest_framework import serializers

from guests.models import Guest


class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = [
            "id",
            "name",
            "document",
            "phone",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
