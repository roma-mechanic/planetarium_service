from django.shortcuts import render
from rest_framework import viewsets

from planetarium.models import ShowTheme, PlanetariumDome
from planetarium.permissions import IsAdminOrIfAuthenticatedReadOnly
from planetarium.serializers import (
    ShowThemeSerializers,
    PlanetariumDomeSerializers,
)


# Create your views here.
class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializers
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializers
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
