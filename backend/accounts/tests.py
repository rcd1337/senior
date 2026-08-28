from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from guests.models import Guest
from reservations.models import Reservation

User = get_user_model()


class AuthAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="atendente", email="atendente@hotel.com", password="teste123"
        )

    def test_login_with_username(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"login": "atendente", "password": "teste123"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_with_email(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"login": "atendente@hotel.com", "password": "teste123"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_login_wrong_password(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"login": "atendente", "password": "senhaerrada"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SeedDemoTestCase(APITestCase):
    def test_seed_creates_known_user_and_is_idempotent(self):
        call_command("seed_demo")
        call_command("seed_demo")

        self.assertEqual(User.objects.filter(username="atendente").count(), 1)
        self.assertEqual(User.objects.filter(username="superuser").count(), 1)
        self.assertEqual(Guest.objects.count(), 5)
        self.assertEqual(Reservation.objects.count(), 3)

        attendant = User.objects.get(username="atendente")
        admin_user = User.objects.get(username="superuser")
        self.assertTrue(attendant.check_password("123"))
        self.assertFalse(attendant.is_superuser)
        self.assertTrue(admin_user.check_password("123"))
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

        names = set(Guest.objects.values_list("name", flat=True))
        self.assertEqual(
            names,
            {
                "Frank Reynolds",
                "Charlie Kelly",
                'Ronald "Mac" McDonald',
                "Dennis Reynolds",
                "Dee Reynolds",
            },
        )

        reserved = Reservation.objects.get(status=Reservation.Status.RESERVED)
        self.assertEqual(reserved.guest.name, 'Ronald "Mac" McDonald')

        in_hotel = Reservation.objects.filter(status=Reservation.Status.CHECKED_IN)
        self.assertEqual(in_hotel.count(), 2)
        by_name = {row.guest.name: row for row in in_hotel}
        self.assertTrue(by_name["Frank Reynolds"].has_car)
        self.assertFalse(by_name["Charlie Kelly"].has_car)

        for name in ("Dennis Reynolds", "Dee Reynolds"):
            self.assertFalse(Guest.objects.get(name=name).reservations.exists())

        for login in (
            "atendente",
            "atendente@exemplo.com",
            "superuser",
            "superuser@exemplo.com",
        ):
            response = self.client.post(
                reverse("token_obtain_pair"),
                {"login": login, "password": "123"},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
