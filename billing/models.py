from django.db import models


class Bill(models.Model):
    reservation = models.ForeignKey("HouseReservation", verbose_name="Счет на оплату бронирования",
                                    on_delete=models.SET_NULL,
                                    null=True, related_name='bill')

    total = models.IntegerField("Итоговая стоимость", default=0)

