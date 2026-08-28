from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from guests.models import Guest
from reservations.models import Reservation

User = get_user_model()


class GuestAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="atendente", email="atendente@hotel.com", password="teste123"
        )
        token = RefreshToken.for_user(self.user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        self.guest = Guest.objects.create(
            name="Maria Silva", document="12345678900", phone="11999990000"
        )

    def test_guest_list_requires_login(self):
        self.client.credentials()
        response = self.client.get(reverse("guest-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_guest(self):
        url = reverse("guest-list")
        payload = {
            "name": "Joao Souza",
            "document": "10987654321",
            "phone": "11888880000",
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Guest.objects.count(), 2)

    def test_search_guest_by_document(self):
        url = reverse("guest-list")
        response = self.client.get(url, {"search": "12345678900"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Maria Silva")

    def test_search_guest_by_name(self):
        url = reverse("guest-list")
        response = self.client.get(url, {"search": "Maria"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_guest_by_phone(self):
        url = reverse("guest-list")
        response = self.client.get(url, {"search": "11999990000"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_checked_in_filter(self):
        Reservation.objects.create(
            guest=self.guest,
            planned_check_in="2026-08-26",
            planned_check_out="2026-08-28",
            status=Reservation.Status.CHECKED_IN,
            checked_in_at=timezone.now(),
        )
        url = reverse("guest-list")
        response = self.client.get(url, {"status": "checked_in"})
        self.assertEqual(len(response.data), 1)

    def test_reserved_filter(self):
        Reservation.objects.create(
            guest=self.guest,
            planned_check_in="2026-08-26",
            planned_check_out="2026-08-28",
            status=Reservation.Status.RESERVED,
        )
        url = reverse("guest-list")
        response = self.client.get(url, {"status": "reserved"})
        self.assertEqual(len(response.data), 1)

    def test_checked_out_filter(self):
        Reservation.objects.create(
            guest=self.guest,
            planned_check_in="2026-08-26",
            planned_check_out="2026-08-28",
            status=Reservation.Status.CHECKED_OUT,
        )
        url = reverse("guest-list")
        response = self.client.get(url, {"status": "checked_out"})
        self.assertEqual(len(response.data), 1)
