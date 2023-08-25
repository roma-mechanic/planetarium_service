import os
import tempfile

from PIL import Image
from django.db.models import F, Count
from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from planetarium.models import (
    AstronomyShow,
    PlanetariumDome,
    ShowSession,
)
from planetarium.serializers import (
    AstronomyShowListSerializer,
    AstronomyShowDetailSerializer,
    ShowSessionListSerializer,
    ShowSessionSerializer,
    ShowSessionDetailSerializer,
)
from planetarium.views import ShowSessionViewSet

ASTRONOMY_SHOW_URL = reverse("planetarium:astronomyshow-list")
SHOW_SESSION_URL = reverse("planetarium:showsession-list")


def detail_url(astro_show_id: int):
    return reverse("planetarium:showsession-detail", args=[astro_show_id])


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


class UnauthentikatedShowSessionTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_requires(self):
        res = self.client.get(SHOW_SESSION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticateShowSessionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "astronaut@astronaut.com", "password"
        )
        self.client.force_authenticate(self.user)

    def test_show_session_list(self):
        sample_show_session()

        res = self.client.get(SHOW_SESSION_URL)

        show_session = ShowSession.objects.all()
        serializer = ShowSessionListSerializer(show_session, many=True)

        print(res.data)
        print(serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            serializer.data[0]["show_time"], res.data[0]["show_time"]
        )
        self.assertEqual(
            serializer.data[0]["planetarium_dome_name"],
            res.data[0]["planetarium_dome_name"],
        )
        self.assertEqual(
            serializer.data[0]["astronomy_show_title"],
            res.data[0]["astronomy_show_title"],
        )
        self.assertEqual(
            serializer.data[0]["astro_show_image"],
            res.data[0]["astro_show_image"],
        )
        self.assertEqual(
            serializer.data[0]["planetarium_dome_capacity"],
            res.data[0]["planetarium_dome_capacity"],
        )

    def test_retrieve_show_session_details(self):
        show_session = sample_show_session()

        url = detail_url(show_session.id)
        res = self.client.get(url)

        serializer = ShowSessionDetailSerializer(show_session)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_show_session_filter_by_date(self):
        sample_show_session()
        sample_show_session(show_time="2022-06-03T14:00:00")

        res = self.client.get(SHOW_SESSION_URL, {"show_time": "2022-06-02"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]["show_time"], "2022-06-02T14:00:00")
        self.assertNotEquals(res.data[0]["show_time"], "2022-06-03T14:00:00")

    def test_show_session_filter_by_astronomy_show_id(self):
        sample_show_session()
        another_astro_show = sample_astronomy_show(
            title="another title",
            description="any description",
            duration=50
        )
        sample_show_session(astronomy_show=another_astro_show)

        res = self.client.get(SHOW_SESSION_URL, {"astronomy_show": f"{another_astro_show.id}"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]["astronomy_show_title"], "another title")
        self.assertNotEquals(res.data[0]["astronomy_show_title"], "test title")

    def test_create_show_session_forbidden(self):
        payload = {
            "show_time": "2022-06-02T14:00:00",
            "astronomy_show": sample_astronomy_show(),
            "planetarium_dome": sample_planetarium_dome(),
        }
        res = self.client.post(SHOW_SESSION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminShowSessionApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_show_session(self):
        astro_show = sample_astronomy_show()
        plan_dome = sample_planetarium_dome()
        payload = {
            "show_time": "2022-06-02T14:00:00",
            "astronomy_show": astro_show.id,
            "planetarium_dome": plan_dome.id,
        }
        res = self.client.post(SHOW_SESSION_URL, payload)
        # print(res.data)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        show_session = ShowSession.objects.get(id=res.data["id"])
        serializer = ShowSessionSerializer(show_session)
        print(serializer.data)
        for key in payload.keys():
            self.assertEqual(payload[key], serializer.data[key])
