from django.contrib import admin
from houses.models import House, HousePicture, HouseFeature


class HousePictureAdminInline(admin.TabularInline):
    model = HousePicture


class HouseAdmin(admin.ModelAdmin):
    model = House
    list_display = ('name',
                    'base_price', 'holidays_multiplier',
                    'created_at',)
    inlines = [HousePictureAdminInline, ]


class HouseFeatureAdmin(admin.ModelAdmin):
    model = HouseFeature
    list_display = ('name', 'icon')


admin.site.register(House, HouseAdmin)
admin.site.register(HouseFeature, HouseFeatureAdmin)
