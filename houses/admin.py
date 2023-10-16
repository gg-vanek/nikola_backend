from django.contrib import admin

from houses.models import House, HousePicture


class HousePictureAdminInline(admin.TabularInline):
    model = HousePicture


class HouseAdmin(admin.ModelAdmin):
    model = House
    list_display = ('name', 'description',
                    'base_price', 'holidays_multiplier',
                    'created_at', 'updated_at',)
    inlines = [HousePictureAdminInline, ]


admin.site.register(House, HouseAdmin)
