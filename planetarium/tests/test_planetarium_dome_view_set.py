from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from planetarium.models import PlanetariumDome
from planetarium.serializers import (
    PlanetariumDomeSerializer,
    PlanetariumDomeListSerializer,
)

PLANETARIUM_DOME_URL = reverse("planetarium:planetariumdome-list")


def detail_url(planetarium_dome_id: int):
    return reverse(
        "planetarium:planetariumdome-detail", args=[planetarium_dome_id]
    )


def sample_planetarium_dome(**params):
    defaults = {
        "name": "test name",
        "address": "test address",
        "city_state_province": "test province",
        "country": "test country",
        "phone": "1234567",
        "website": "https://www.testsite.com",
        "rows": 10,
        "seats_in_row": 10,
    }
    defaults.update(params)
    return PlanetariumDome.objects.create(**defaults)


class UnauthentikatedPlanetariumDomeTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_requires(self):
        res = self.client.get(PLANETARIUM_DOME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatePlanetariumDomeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "goblin@goblin.com", "password"
        )
        self.client.force_authenticate(self.user)

    def test_planetarium_dome_list(self):
        sample_planetarium_dome()

        res = self.client.get(PLANETARIUM_DOME_URL)
        dome = PlanetariumDome.objects.all()
        serializer = PlanetariumDomeListSerializer(dome, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_with_country(self):
        planet_dome1 = sample_planetarium_dome(country="country_1")
        planet_dome2 = sample_planetarium_dome(country="country_2")

        serializer1 = PlanetariumDomeListSerializer(planet_dome1)
        serializer2 = PlanetariumDomeListSerializer(planet_dome2)

        res = self.client.get(
            PLANETARIUM_DOME_URL, {"country": f"{planet_dome1.country}"}
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])

    def test_retrieve_planetarium_dome_details(self):
        plan_dome = sample_planetarium_dome()
        serializer = PlanetariumDomeSerializer(plan_dome)
        url = detail_url(plan_dome.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_planetarium_dome_forbidden(self):
        payload = {
            "name": "test name",
            "address": "test address",
            "city_state_province": "test province",
            "country": "test country",
            "phone": "1234567",
            "website": "https://www.testsite.com",
            "rows": 10,
            "seats_in_row": 10,
        }
        res = self.client.post(PLANETARIUM_DOME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminMovieApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "gobin@doblin.com", "password", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_planetarium_dome(self):
        payload = {
            "name": "test name",
            "address": "test address",
            "city_state_province": "test province",
            "country": "test country",
            "phone": "1234567",
            "website": "https://www.testserver.com",
            "rows": 10,
            "seats_in_row": 10,
        }
        res = self.client.post(PLANETARIUM_DOME_URL, payload)
        plan_dome = PlanetariumDome.objects.get(id=res.data["id"])
        serializer = PlanetariumDomeSerializer(plan_dome)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["name"], getattr(plan_dome, "name"))
        self.assertEqual(payload["address"], getattr(plan_dome, "address"))
        self.assertEqual(
            payload["city_state_province"],
            getattr(plan_dome, "city_state_province"),
        )
        self.assertEqual(payload["country"], getattr(plan_dome, "country"))
        self.assertEqual(payload["phone"], getattr(plan_dome, "phone"))
        self.assertEqual(payload["website"], getattr(plan_dome, "website"))
        self.assertEqual(payload["rows"], getattr(plan_dome, "rows"))
        self.assertEqual(
            payload["seats_in_row"], getattr(plan_dome, "seats_in_row")
        )
        self.assertEqual(serializer.data, res.data)
