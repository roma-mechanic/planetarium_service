from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from planetarium.models import (
    ShowTheme,
    PlanetariumDome,
    AstronomyShow,
    ShowSession,
    Reservation,
    Ticket,
)


class ShowThemeSerializers(serializers.ModelSerializer):
    class Meta:
        model = ShowTheme
        fields = ("id", "name")


class PlanetariumDomeSerializer(serializers.ModelSerializer):
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


class PlanetariumDomeListSerializer(PlanetariumDomeSerializer):
    class Meta:
        model = PlanetariumDome
        fields = ("id", "name", "address", "country", "seating_capacity")


class AstronomyShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = AstronomyShow
        fields = ("id", "title", "description", "duration", "theme", "image")


class AstronomyShowListSerializer(AstronomyShowSerializer):
    theme = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )

    class Meta:
        model = AstronomyShow
        fields = ("id", "title", "description", "duration", "theme", "image")


class AstronomyShowDetailSerializer(AstronomyShowSerializer):
    theme = ShowThemeSerializers(many=True, read_only=True)

    class Meta:
        model = AstronomyShow
        fields = ("id", "title", "description", "duration", "theme", "image")


class AstronomyShowImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AstronomyShow
        fields = ("id", "image")


class ShowSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowSession
        fields = ("id", "astronomy_show", "planetarium_dome", "show_time")


class ShowSessionListSerializer(serializers.ModelSerializer):
    planetarium_dome_name = serializers.CharField(
        source="planetarium_dome.name", read_only=True
    )
    astronomy_show_title = serializers.CharField(
        source="astronomy_show.title", read_only=True
    )
    astro_show_image = serializers.ImageField(
        source="astronomy_show.image", read_only=True
    )
    planetarium_dome_capacity = serializers.IntegerField(
        source="planetarium_dome.seating_capacity", read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = ShowSession
        fields = (
            "id",
            "show_time",
            "astronomy_show_title",
            "planetarium_dome_name",
            "astro_show_image",
            "planetarium_dome_capacity",
            "tickets_available",
        )


class ShowSessionShortListSerializer(ShowSessionListSerializer):
    class Meta:
        model = ShowSession
        fields = ("astronomy_show_title",)


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["show_session"].planetarium_dome,
            ValidationError,
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "show_session")


class TicketListSerializer(TicketSerializer):
    astronomy_show_name = serializers.CharField(
        source="show_session.astronomy_show.title", read_only=True
    )
    planetarium_dome_name = serializers.CharField(
        source="show_session.planetarium_dome.name", read_only=True
    )
    show_time = serializers.DateTimeField(
        source="show_session.show_time", read_only=True
    )
    reservation_date = serializers.CharField(
        source="reservation.created_at", read_only=True
    )
    reservation_owner = serializers.CharField(
        source="reservation.user", read_only=True
    )

    class Meta:
        model = Ticket
        fields = (
            "id",
            "show_time",
            "astronomy_show_name",
            "planetarium_dome_name",
            "reservation_date",
            "reservation_owner",
            "row",
            "seat",
        )


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class ShowSessionDetailSerializer(serializers.ModelSerializer):
    planetarium_dome = PlanetariumDomeSerializer(many=False, read_only=True)
    astronomy_show = AstronomyShowListSerializer(many=False, read_only=True)
    taken_places = TicketSeatsSerializer(
        source="tickets",
        many=True,
        read_only=True,
    )

    class Meta:
        model = ShowSession
        fields = (
            "id",
            "show_time",
            "astronomy_show",
            "planetarium_dome",
            "taken_places",
        )


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_null=False)

    class Meta:
        model = Reservation
        fields = ("id", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
            return reservation


class ReservationListSerializer(ReservationSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
    reservation_owner = serializers.CharField(source="user", required=True)

    class Meta:
        model = Reservation
        fields = ("id", "tickets", "created_at", "reservation_owner")
