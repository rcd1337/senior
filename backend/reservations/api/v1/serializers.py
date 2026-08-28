from rest_framework import serializers

from guests.api.v1.serializers import GuestSerializer
from reservations.models import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    guest_detail = GuestSerializer(source="guest", read_only=True)

    class Meta:
        model = Reservation
        fields = [
            "id",
            "guest",
            "guest_detail",
            "planned_check_in",
            "planned_check_out",
            "has_car",
            "status",
            "checked_in_at",
            "checked_out_at",
            "bill",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "checked_in_at",
            "checked_out_at",
            "bill",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        check_in = attrs.get("planned_check_in")
        check_out = attrs.get("planned_check_out")
        if check_in and check_out and check_out <= check_in:
            raise serializers.ValidationError("A data de checkout deve ser depois do check-in.")
        return attrs
