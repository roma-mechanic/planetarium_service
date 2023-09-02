from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from planetarium.models import (
    Reservation,
    Ticket,
    PlanetariumDome,
    ShowSession,
    AstronomyShow,
)
from planetarium.serializers import (
    ReservationListSerializer,
    ReservationSerializer,
)

RESERVATION_URL = reverse("planetarium:reservation-list")


def detail_url(reservation_id: int):
    return reverse("planetarium:reservation-detail", args=[reservation_id])


def sample_astronomy_show(**params):
    defaults = {
        "title": "test title",
        "description": "test description",
        "duration": 45,
    }
    defaults.update(params)
    return AstronomyShow.objects.create(**defaults)


def sample_planetarium_dome(**param):
    default = {
        "name": "planetarium",
        "address": "any address",
        "city_state_province": "any province",
        "country": "any country",
        "rows": 10,
        "seats_in_row": 6,
    }
    default.update(param)
    return PlanetariumDome.objects.create(**default)


def sample_show_session(**params):
    defaults = {
        "show_time": "2022-06-02T14:00:00",
        "astronomy_show": sample_astronomy_show(),
        "planetarium_dome": sample_planetarium_dome(),
    }
    defaults.update(params)
    return ShowSession.objects.create(**defaults)


class UnAuthentikatedReservationTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_requires(self):
        res = self.client.get(RESERVATION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticateReservationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "astronaut@astronaut.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.reservation = Reservation.objects.create(
            created_at="", user=self.user
        )
        self.ticket = Ticket.objects.create(
            row=1,
            seat=1,
            reservation=self.reservation,
            show_session=sample_show_session(),
        )

    def test_reservation_list(self):
        self.reservation.tickets.add(self.ticket)

        res = self.client.get(RESERVATION_URL)
        serializer = ReservationListSerializer(self.reservation)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"][0], serializer.data)

    def test_retrieve_reservation_details(self):
        self.reservation.tickets.add(self.ticket)

        url = detail_url(self.reservation.id)
        res = self.client.get(url)

        serializer = ReservationListSerializer(self.reservation)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_movie_forbidden(self):
        payload = {
            "create_at": "",
            "user": "test user",
        }
        res = self.client.post(RESERVATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
