from django.contrib import admin

from planetarium.models import (
    ShowTheme,
    PlanetariumDome,
    AstronomyShow,
    ShowSession,
    Reservation,
    Ticket,
)

admin.site.register(ShowTheme)
admin.site.register(PlanetariumDome)
admin.site.register(AstronomyShow)
admin.site.register(ShowSession)
admin.site.register(Reservation)
admin.site.register(Ticket)
