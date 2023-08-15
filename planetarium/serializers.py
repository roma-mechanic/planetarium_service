from rest_framework import serializers

from planetarium.models import ShowTheme


class ShowThemeSerializers(serializers.ModelSerializer):
    class Meta:
        model = ShowTheme
        fields = ("id", "name")
