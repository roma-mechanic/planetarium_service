import os
import tempfile

from PIL import Image
from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from planetarium.models import AstronomyShow, ShowTheme, PlanetariumDome, ShowSession
from planetarium.serializers import (
    AstronomyShowListSerializer,
    AstronomyShowDetailSerializer,
)

ASTRONOMY_SHOW_URL = reverse("planetarium:astronomyshow-list")
SHOW_SESSION_URL = reverse("planetarium:showsession-list")


def detail_url(astro_show_id: int):
    return reverse(
        "planetarium:astronomyshow-detail", args=[astro_show_id]
    )


def image_upload_url(astro_show_id):
    """Return URL for recipe image upload"""
    return reverse("planetarium:astronomyshow-upload-image", args=[astro_show_id])


def sample_astronomy_show(**params):
    defaults = {
        "title": "test title",
        "description": "test description",
        "duration": 45,
    }
    defaults.update(params)
    return AstronomyShow.objects.create(**defaults)


def sample_show_session(**params):
    planetarium_dome = PlanetariumDome.objects.create(
        name="planetarium",
        address="any address",
        city_state_province="any province",
        country="any country",
        rows=20,
        seats_in_row=20
    )
    defaults = {
        "show_time": "2022-06-02 14:00:00",
        "astronomy_show": sample_astronomy_show(),
        "planetarium_dome": planetarium_dome,
    }
    defaults.update(params)

    return ShowSession.objects.create(**defaults)


def sample_theme(**params):
    default = {"name": "test theme"}
    default.update(params)
    return ShowTheme.objects.create(**default)


class UnauthentikatedAstronomyShowTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_requires(self):
        res = self.client.get(ASTRONOMY_SHOW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticateAstronomyShowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "astronaut@astronaut.com", "password"
        )
        self.client.force_authenticate(self.user)

    def test_astronomy_show_list(self):
        sample_astronomy_show()

        res = self.client.get(ASTRONOMY_SHOW_URL)

        astro_show = AstronomyShow.objects.order_by("id")
        serializer = AstronomyShowListSerializer(astro_show, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_by_title(self):
        astro_show_1 = sample_astronomy_show(title="title_1")
        astro_show_2 = sample_astronomy_show(title="title_2")

        res = self.client.get(ASTRONOMY_SHOW_URL, {"title": "title_1"})
        serializer_1 = AstronomyShowListSerializer(astro_show_1)
        serializer_2 = AstronomyShowListSerializer(astro_show_2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, res.data)
        self.assertNotIn(serializer_2.data, res.data)

    def test_filter_by_theme(self):
        astro_show_1 = sample_astronomy_show(title="title_1")
        astro_show_2 = sample_astronomy_show(title="title_2")

        theme_1 = sample_theme(name="test theme 1")
        theme_2 = sample_theme(name="test theme 2")

        astro_show_1.theme.add(theme_1, theme_2)

        res = self.client.get(
            ASTRONOMY_SHOW_URL, {"theme": f"{theme_1.id},{theme_2.id}"}
        )
        serializer_1 = AstronomyShowListSerializer(astro_show_1)
        serializer_2 = AstronomyShowListSerializer(astro_show_2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, res.data)
        self.assertNotIn(serializer_2.data, res.data)

    def test_retrieve_astro_show_details(self):
        astro_show = sample_astronomy_show()
        astro_show.theme.add(sample_theme())

        url = detail_url(astro_show.id)
        res = self.client.get(url)

        serializer = AstronomyShowDetailSerializer(astro_show)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_astro_show_forbidden(self):
        payload = {
            "title": "test show",
            "description": "Description",
            "duration": 90,
        }
        res = self.client.post(ASTRONOMY_SHOW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAstronomyShowApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_astro_show(self):
        payload = {
            "title": "test title",
            "description": "Description",
            "duration": 40,
        }
        res = self.client.post(ASTRONOMY_SHOW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        astro_show = AstronomyShow.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(astro_show, key))

    def test_create_astro_show_with_show_theme(self):
        theme_1 = sample_theme(name="test name 1")
        theme_2 = sample_theme(name="test name 2")

        payload = {
            "title": "title 1",
            "description": "Full description of astro show",
            "duration": 30,
            "theme": [theme_2.id, theme_1.id]
        }
        res = self.client.post(ASTRONOMY_SHOW_URL, payload)
        astro_show = AstronomyShow.objects.get(id=res.data["id"])
        theme = astro_show.theme.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(theme.count(), 2)
        self.assertIn(theme_1, theme)
        self.assertIn(theme_2, theme)


class MovieImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "astronaut@myproject.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.astronomy_show = sample_astronomy_show()
        self.theme = sample_theme()
        self.show_session = sample_show_session(astronomy_show=self.astronomy_show)

    def tearDown(self):
        self.astronomy_show.image.delete()

    def test_upload_image_to_astro_show(self):
        """Test uploading an image to movie"""
        url = image_upload_url(self.astronomy_show.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.astronomy_show.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.astronomy_show.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.astronomy_show.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_astro_show_list_should_not_work(self):
        url = ASTRONOMY_SHOW_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "title": "Title",
                    "description": "Description",
                    "duration": 90,
                    "theme": [1],
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        astro_show = AstronomyShow.objects.get(title="Title")
        self.assertFalse(astro_show.image)

    def test_image_url_is_shown_on_astro_show_detail(self):
        url = image_upload_url(self.astronomy_show.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_url(self.astronomy_show.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_astro_show_list(self):
        url = image_upload_url(self.astronomy_show.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(ASTRONOMY_SHOW_URL)

        self.assertIn("image", res.data[0].keys())

    def test_image_url_is_shown_on_show_session_detail(self):
        url = image_upload_url(self.astronomy_show.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(SHOW_SESSION_URL)

        self.assertIn("astro_show_image", res.data[0].keys())