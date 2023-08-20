from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.test import APIClient

from planetarium.models import ShowTheme
from planetarium.serializers import ShowThemeSerializers

SHOW_THEME_URL = reverse("planetarium:showtheme-list")


def detail_url(show_theme_id: int):
    return reverse("planetarium:showtheme-detail", args=[show_theme_id])


def sample_show_theme(**params):
    defaults = {"name": "test name"}
    defaults.update(params)
    return ShowTheme.objects.create(**defaults)


class UnauthentikatedShowThemeTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_requires(self):
        res = self.client.get(SHOW_THEME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticateShowThemeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "goblin@goblin.com", "password"
        )
        self.client.force_authenticate(self.user)
        pagination_class = PageNumberPagination

    def test_show_theme_list(self):
        sample_show_theme()
        res = self.client.get(SHOW_THEME_URL)
        show_theme = ShowTheme.objects.all()
        serializer = ShowThemeSerializers(show_theme, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_show_theme_details(self):
        theme = sample_show_theme()
        serializer = ShowThemeSerializers(theme)
        url = detail_url(theme.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_show_theme_forbidden(self):
        payload = {
            "name": "test name",
        }
        res = self.client.post(SHOW_THEME_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminShowThemeApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "star_tramp@star.com", "password", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_show_theme(self):
        payload = {"name": "any name"}
        res = self.client.post(SHOW_THEME_URL, payload)
        theme = ShowTheme.objects.get(id=res.data["id"])
        serializer = ShowThemeSerializers(theme)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["name"], getattr(theme, "name"))
