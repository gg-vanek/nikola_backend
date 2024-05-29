from django.core.exceptions import ValidationError
from django.db import models

from house_reservations_billing.models.constants import FIXED_VALUE_DISCOUNT, PERCENTAGE_DISCOUNT


class HouseReservationPromoCode(models.Model):
    DISCOUNT_TYPE_CHOICES = {
        FIXED_VALUE_DISCOUNT: "Скидка на фиксированную сумму",
        PERCENTAGE_DISCOUNT: "Скидка на процент от чека"
    }

    code = models.CharField(max_length=255, verbose_name="Промокод", unique=True)
    enabled = models.BooleanField(default=True)

    discount_type = models.CharField(max_length=15, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.IntegerField()

    client = models.ForeignKey("clients.Client", default=None, null=True, blank=True, on_delete=models.CASCADE)
    max_use_times = models.IntegerField(default=1)
    minimal_bill_value = models.IntegerField(default=0)

    issuance_datetime = models.DateTimeField(default=None, null=True, blank=True)
    expiration_datetime = models.DateTimeField(default=None, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if self.discount_type == PERCENTAGE_DISCOUNT:
            if not (0 <= self.discount_value <= 100):
                raise ValidationError('Промокод с типом "PERCENTAGE_DISCOUNT" '
                                      'должен иметь значение в промежутке от 0 до 100')

        if self.issuance_datetime and self.expiration_datetime:
            if self.issuance_datetime >= self.expiration_datetime:
                raise ValidationError(f'Некорректные даты действия промокода. '
                                      f'не выполнено self.issuance_datetime < self.expiration_datetime: '
                                      f'({self.issuance_datetime.strftime("%d-%m-%Y %H:%M")} '
                                      f'< {self.expiration_datetime.strftime("%d-%m-%Y %H:%M")})')

    def __str__(self):
        s = f"{self.code}: -{self.discount_value}"
        if self.discount_type == FIXED_VALUE_DISCOUNT:
            s += " руб."
        elif self.discount_type == PERCENTAGE_DISCOUNT:
            s += "%"
        else:
            s += " (!!!ПРОМОКОД С НЕКОРРЕКТНЫМ ТИПОМ!!!)"
        return s
