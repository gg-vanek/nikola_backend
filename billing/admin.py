from django.contrib import admin
from billing.models import HouseReservationBill, HouseReservationPromoCode


class HouseReservationBillAdmin(admin.ModelAdmin):
    model = HouseReservationBill
    list_display = ('reservation',
                    'total',)


class HouseReservationPromoCodeAdmin(admin.ModelAdmin):
    model = HouseReservationPromoCode
    list_display = ("id", "code",
                    "enabled",
                    "discount_type",
                    "discount_value",
                    "client",
                    "max_use_times",
                    "issuance_datetime",
                    "expiration_datetime",)


admin.site.register(HouseReservationBill, HouseReservationBillAdmin)
admin.site.register(HouseReservationPromoCode, HouseReservationPromoCodeAdmin)
