from django.contrib import admin

from houses.models import House, HousePicture, HouseReservation, HouseFeature


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


class HouseFeatureAdmin(admin.ModelAdmin):
    model = HouseFeature
    list_display = ('name', 'icon')


admin.site.register(House, HouseAdmin)
admin.site.register(HouseReservation, HouseReservationAdmin)
admin.site.register(HouseFeature, HouseFeatureAdmin)
