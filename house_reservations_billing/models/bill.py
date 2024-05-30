from django.core.validators import MinValueValidator
from django.db import models

from house_reservations_billing.json_mappers import (
    ChronologicalPositionsEncoder,
    ChronologicalPositionsDecoder,
    NonChronologicalPositionsEncoder,
    NonChronologicalPositionsDecoder,
)
from house_reservations_billing.services.bill import initialize_bill


class HouseReservationBill(models.Model):
    reservation = models.OneToOneField(
        "house_reservations.HouseReservation",
        verbose_name="Счет на оплату бронирования домика",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='bill',
    )

    total = models.IntegerField("Итоговая стоимость", validators=[MinValueValidator(100)])

    chronological_positions = models.JSONField(
        verbose_name="Хронологически упорядоченные позиции",
        default=dict,
        blank=True,
        encoder=ChronologicalPositionsEncoder,
        decoder=ChronologicalPositionsDecoder,
    )
    non_chronological_positions = models.JSONField(
        verbose_name="Хронологически неупорядоченные позиции",
        default=dict,
        blank=True,
        encoder=NonChronologicalPositionsEncoder,
        decoder=NonChronologicalPositionsDecoder,
    )

    promo_code = models.ForeignKey(
        verbose_name="Промокод",
        to="HouseReservationPromoCode",
        on_delete=models.SET_NULL,
        related_name='bills',
        default=None,
        null=True,
        blank=True,
    )

    paid = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Счет на оплату бронирования домика"
        verbose_name_plural = 'Счета на оплату бронирования домиков'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initialize_bill(self)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Счет на оплату бронирования ({self.reservation.id})"
