from django.urls import path, include
from rest_framework import routers

from planetarium.views import ShowThemeViewSet, PlanetariumDomeViewSet

router = routers.DefaultRouter()
router.register("show_theme", ShowThemeViewSet)
router.register("planetarium_dome", PlanetariumDomeViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "planetarium"
