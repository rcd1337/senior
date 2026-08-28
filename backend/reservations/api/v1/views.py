from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from reservations.models import Reservation
from reservations.services import build_bill, checkin_alert

from .serializers import ReservationSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    """Cria e lê reservas. Status só muda por check-in/check-out; sem PUT/PATCH/DELETE."""

    serializer_class = ReservationSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return Reservation.objects.select_related("guest").all()

    @action(detail=True, methods=["post"], url_path="check-in")
    def check_in(self, request, pk=None):
        reservation = self.get_object()
        if reservation.status != Reservation.Status.RESERVED:
            return Response(
                {"detail": "Só é possível fazer check-in de uma reserva pendente."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.localtime()
        reservation.status = Reservation.Status.CHECKED_IN
        reservation.checked_in_at = now
        reservation.save(update_fields=["status", "checked_in_at"])

        data = self.get_serializer(reservation).data
        data["alert"] = checkin_alert(now)
        return Response(data)

    @action(detail=True, methods=["post"], url_path="check-out")
    def check_out(self, request, pk=None):
        reservation = self.get_object()
        if reservation.status != Reservation.Status.CHECKED_IN:
            return Response(
                {"detail": "Só é possível fazer check-out de hóspede hospedado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.localtime()
        bill = build_bill(
            reservation.planned_check_in,
            reservation.planned_check_out,
            reservation.has_car,
            now,
        )
        reservation.status = Reservation.Status.CHECKED_OUT
        reservation.checked_out_at = now
        reservation.bill = bill
        reservation.save(update_fields=["status", "checked_out_at", "bill"])
        return Response(self.get_serializer(reservation).data)
