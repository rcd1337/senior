from django.contrib import admin

from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "guest",
        "planned_check_in",
        "planned_check_out",
        "status",
    ]
    list_filter = [
        "status",
    ]
    search_fields = [
        "guest__name",
        "guest__document",
    ]
