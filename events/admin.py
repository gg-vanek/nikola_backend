from django.contrib import admin

from events.models import Event


class EventAdmin(admin.ModelAdmin):
    model = Event
    list_display = ('name', 'multiplier', 'start_date', 'end_date')


admin.site.register(Event, EventAdmin)
