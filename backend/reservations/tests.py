from datetime import date, datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import SimpleTestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from guests.models import Guest
from reservations.models import Reservation
from reservations.services import (
    build_bill,
    checkin_alert,
    daily_rate,
    late_checkout_fee,
    parking_rate,
    stay_dates,
)

User = get_user_model()


class PricingRulesTests(SimpleTestCase):
    def test_weekday_daily_is_120(self):
        wednesday = date(2026, 8, 26)
        self.assertEqual(daily_rate(wednesday), Decimal("120.00"))

    def test_weekend_daily_is_180(self):
        saturday = date(2026, 8, 29)
        self.assertEqual(daily_rate(saturday), Decimal("180.00"))

    def test_parking_weekday_and_weekend(self):
        self.assertEqual(parking_rate(date(2026, 8, 26)), Decimal("15.00"))
        self.assertEqual(parking_rate(date(2026, 8, 29)), Decimal("20.00"))

    def test_stay_counts_nights(self):
        days = stay_dates(date(2026, 8, 26), date(2026, 8, 28))
        self.assertEqual(days, [date(2026, 8, 26), date(2026, 8, 27)])

    def test_checkin_before_14h_emits_alert(self):
        alert = checkin_alert(datetime(2026, 8, 26, 10, 0))
        self.assertIsNotNone(alert)

    def test_checkin_after_14h_has_no_alert(self):
        alert = checkin_alert(datetime(2026, 8, 26, 14, 0))
        self.assertIsNone(alert)

    def test_late_checkout_weekend_uses_half_of_180(self):
        fee = late_checkout_fee(datetime(2026, 8, 29, 13, 0))
        self.assertEqual(fee, Decimal("90.00"))

    def test_checkout_before_noon_has_no_fee(self):
        fee = late_checkout_fee(datetime(2026, 8, 26, 11, 59))
        self.assertEqual(fee, Decimal("0.00"))

    def test_bill_with_car_two_weekdays(self):
        bill = build_bill(
            date(2026, 8, 26),
            date(2026, 8, 28),
            True,
            datetime(2026, 8, 28, 11, 0),
        )
        self.assertEqual(bill["total"], "270.00")
        self.assertEqual(bill["late_checkout_fee"], "0.00")
        self.assertEqual(len(bill["items"]), 2)


class ReservationAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="atendente", email="atendente@hotel.com", password="teste123"
        )
        token = RefreshToken.for_user(self.user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        self.guest = Guest.objects.create(
            name="Maria Silva", document="12345678900", phone="11999990000"
        )

    def test_create_reservation(self):
        url = reverse("reservation-list")
        payload = {
            "guest": self.guest.id,
            "planned_check_in": "2026-08-26",
            "planned_check_out": "2026-08-28",
            "has_car": True,
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "reserved")

    def test_rejects_checkout_on_or_before_checkin(self):
        url = reverse("reservation-list")
        payload = {
            "guest": self.guest.id,
            "planned_check_in": "2026-08-28",
            "planned_check_out": "2026-08-26",
            "has_car": False,
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Reservation.objects.count(), 0)

    def test_db_constraint_rejects_invalid_dates(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Reservation.objects.create(
                guest=self.guest,
                planned_check_in="2026-08-28",
                planned_check_out="2026-08-26",
            )

    def test_checkin_and_checkout_return_bill(self):
        reservation = Reservation.objects.create(
            guest=self.guest,
            planned_check_in="2026-08-26",
            planned_check_out="2026-08-28",
            has_car=False,
        )
        checkin_url = reverse("reservation-check-in", kwargs={"pk": reservation.pk})
        checkout_url = reverse("reservation-check-out", kwargs={"pk": reservation.pk})

        checkin = self.client.post(checkin_url)
        self.assertEqual(checkin.status_code, status.HTTP_200_OK)
        self.assertEqual(checkin.data["status"], "checked_in")
        self.assertIn("alert", checkin.data)

        checkout = self.client.post(checkout_url)
        self.assertEqual(checkout.status_code, status.HTTP_200_OK)
        self.assertEqual(checkout.data["status"], "checked_out")
        self.assertIsNotNone(checkout.data["bill"])
        self.assertIn("total", checkout.data["bill"])
        self.assertIn("items", checkout.data["bill"])

    def test_checkin_rejects_if_not_reserved(self):
        reservation = Reservation.objects.create(
            guest=self.guest,
            planned_check_in="2026-08-26",
            planned_check_out="2026-08-28",
            status=Reservation.Status.CHECKED_IN,
            checked_in_at=timezone.now(),
        )
        url = reverse("reservation-check-in", kwargs={"pk": reservation.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_checkout_rejects_if_not_checked_in(self):
        reservation = Reservation.objects.create(
            guest=self.guest,
            planned_check_in="2026-08-26",
            planned_check_out="2026-08-28",
        )
        url = reverse("reservation-check-out", kwargs={"pk": reservation.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
