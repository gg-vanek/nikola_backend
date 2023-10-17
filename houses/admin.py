from django.contrib import admin

from houses.models import House, HousePicture, HouseReservation


class HousePictureAdminInline(admin.TabularInline):
    model = HousePicture


class HouseAdmin(admin.ModelAdmin):
    model = House
    list_display = ('name', 'description',
                    'base_price', 'holidays_multiplier',
                    'created_at', 'updated_at',)
    inlines = [HousePictureAdminInline, ]


class HouseReservationAdmin(admin.ModelAdmin):
    model = HouseReservation
    list_display = ('house', 'client',
                    'check_in_datetime', 'check_out_datetime',
                    'price', 'cancelled',
                    'created_at', 'updated_at',)


admin.site.register(House, HouseAdmin)
admin.site.register(HouseReservation, HouseReservationAdmin)
