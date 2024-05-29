from django.db import models


class HouseReservation(models.Model):

    def __init__(self, *args, **kwargs):
        promo_code = None
        if "promo_code" in kwargs:
            promo_code = kwargs.pop("promo_code")

        super().__init__(*args, **kwargs)

        if not hasattr(self, "bill") or not self.bill:
            self.bill = HouseReservationBill(reservation=self, promo_code=promo_code)
