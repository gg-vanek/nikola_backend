from django.contrib import admin
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter

from house_reservations.models import HouseReservation


class HouseReservationAdmin(admin.ModelAdmin):
    list_filter = (
        ('cancelled', DropdownFilter),
        ('house', RelatedDropdownFilter),
    )
    model = HouseReservation
    list_display = ('house', 'client',
                    'check_in_datetime', 'check_out_datetime',
                    'price', 'cancelled',
                    'created_at', 'updated_at',)
    ordering = ("house", "check_in_datetime")


admin.site.register(HouseReservation, HouseReservationAdmin)
