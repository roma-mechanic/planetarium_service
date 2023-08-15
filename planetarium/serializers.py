from rest_framework import serializers

from planetarium.models import ShowTheme, PlanetariumDome


class ShowThemeSerializers(serializers.ModelSerializer):
    class Meta:
        model = ShowTheme
        fields = ("id", "name")


class PlanetariumDomeSerializers(serializers.ModelSerializer):
    class Meta:
        model = PlanetariumDome
        fields = (
            "id",
            "name",
            "address",
            "city_state_province",
            "country",
            "phone",
            "website",
            "rows",
            "seats_in_row",
            "seating_capacity",
        )
