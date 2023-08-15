from django.shortcuts import render
from rest_framework import viewsets

from planetarium.models import ShowTheme
from planetarium.permissions import IsAdminOrIfAuthenticatedReadOnly
from planetarium.serializers import ShowThemeSerializers


# Create your views here.
class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializers
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
