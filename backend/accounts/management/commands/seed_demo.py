from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from guests.models import Guest
from reservations.models import Reservation

User = get_user_model()

DEMO_PASSWORD = "123"

USERS = (
    {
        "username": "atendente",
        "email": "atendente@exemplo.com",
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "username": "superuser",
        "email": "superuser@exemplo.com",
        "is_staff": True,
        "is_superuser": True,
    },
)


class Command(BaseCommand):
    help = "Usuários conhecidos e hóspedes/reservas mínimos para testar a recepção."

    def handle(self, *args, **options):
        for spec in USERS:
            self._upsert_user(**spec)

        today = timezone.localdate()
        now = timezone.now()
        specs = [
            {
                "name": "Frank Reynolds",
                "document": "11111111111",
                "phone": "11988880001",
                "reservation": {
                    "planned_check_in": today - timedelta(days=1),
                    "planned_check_out": today + timedelta(days=1),
                    "has_car": True,
                    "status": Reservation.Status.CHECKED_IN,
                    "checked_in_at": now,
                },
            },
            {
                "name": "Charlie Kelly",
                "document": "22222222222",
                "phone": "11988880002",
                "reservation": {
                    "planned_check_in": today - timedelta(days=1),
                    "planned_check_out": today + timedelta(days=1),
                    "has_car": False,
                    "status": Reservation.Status.CHECKED_IN,
                    "checked_in_at": now,
                },
            },
            {
                "name": 'Ronald "Mac" McDonald',
                "document": "33333333333",
                "phone": "11988880003",
                "reservation": {
                    "planned_check_in": today,
                    "planned_check_out": today + timedelta(days=2),
                    "has_car": False,
                    "status": Reservation.Status.RESERVED,
                },
            },
            {
                "name": "Dennis Reynolds",
                "document": "44444444444",
                "phone": "11988880004",
                "reservation": None,
            },
            {
                "name": "Dee Reynolds",
                "document": "55555555555",
                "phone": "11988880005",
                "reservation": None,
            },
        ]

        for spec in specs:
            reservation_data = spec.pop("reservation")
            guest, created = Guest.objects.get_or_create(
                document=spec["document"],
                defaults=spec,
            )
            if not created:
                guest.name = spec["name"]
                guest.phone = spec["phone"]
                guest.save(update_fields=["name", "phone"])
            self._sync_reservation(guest, reservation_data)

        self.stdout.write("Hóspedes e reservas de demonstração ok.")

    def _sync_reservation(self, guest, reservation_data):
        """Idempotente: a ficha demo fica no estado deste comando."""
        if reservation_data is None:
            guest.reservations.all().delete()
            return

        extras = {"checked_in_at": None, "checked_out_at": None, "bill": None}
        extras.update(reservation_data)
        reservation = guest.reservations.order_by("pk").first()
        if reservation is None:
            Reservation.objects.create(guest=guest, **extras)
        else:
            for field, value in extras.items():
                setattr(reservation, field, value)
            reservation.save()
            guest.reservations.exclude(pk=reservation.pk).delete()

    def _upsert_user(self, username, email, is_staff, is_superuser):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": is_staff,
                "is_superuser": is_superuser,
            },
        )
        user.email = email
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.set_password(DEMO_PASSWORD)
        user.save()
        role = "superuser" if is_superuser else "atendente"
        self.stdout.write(
            f"{role.capitalize()} {'criado' if created else 'atualizado'}: "
            f"{username} / {email} / {DEMO_PASSWORD}"
        )
