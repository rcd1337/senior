from django.db.models import Q
from rest_framework import viewsets

from guests.models import Guest
from reservations.models import Reservation

from .serializers import GuestSerializer


class GuestViewSet(viewsets.ModelViewSet):
    """Filtro: `search` (nome, documento, telefone) e `status` da reserva."""

    serializer_class = GuestSerializer

    def get_queryset(self):
        qs = Guest.objects.all()
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(document__icontains=search)
                | Q(phone__icontains=search)
            )

        status = self.request.query_params.get("status")
        if status in Reservation.Status.values:
            qs = qs.filter(reservations__status=status).distinct()
        return qs
