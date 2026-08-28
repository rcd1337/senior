from django.db import models

from guests.models import Guest


class Reservation(models.Model):

    class Status(models.TextChoices):
        RESERVED = "reserved", "Reservado"
        CHECKED_IN = "checked_in", "Hospedado"
        CHECKED_OUT = "checked_out", "Check-out realizado"

    guest = models.ForeignKey(Guest, related_name="reservations", on_delete=models.PROTECT)
    planned_check_in = models.DateField()
    planned_check_out = models.DateField()
    has_car = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RESERVED)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_out_at = models.DateTimeField(null=True, blank=True)
    bill = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(planned_check_out__gt=models.F("planned_check_in")),
                name="check_out_after_check_in",
            )
        ]

    def __str__(self):
        return f"Reserva {self.pk} - {self.guest} ({self.status})"
