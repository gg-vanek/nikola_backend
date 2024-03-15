from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import RangeOperators, RangeBoundary
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

from django.db import models
from django.db.models import Q
from django.utils.timezone import now

from core.models import Pricing

from clients.models import Client
from house_reservations.services.sql_functions import TsTzRange


class HouseReservation(models.Model):
    house = models.ForeignKey("houses.House", verbose_name="Домик", on_delete=models.SET_NULL,
                              null=True, related_name='reservations')
    client = models.ForeignKey(Client, verbose_name="Клиент", on_delete=models.SET_NULL,
                               null=True, related_name='reservations')

    check_in_datetime = models.DateTimeField("Дата и время заезда")
    check_out_datetime = models.DateTimeField("Дата и время выезда")
    extra_persons_amount = models.IntegerField(
        "Дополнительное количество человек для проживания в домике",
        default=0,
        validators=[
            MinValueValidator(0, message="В бронировании нельзя указывать отрицательное количество человек"),
        ])

    price = models.IntegerField("Стоимость", blank=True)

    preferred_contact = models.CharField("Предпочтительный способ связи", max_length=255)
    comment = models.CharField("Комментарий", max_length=511)

    cancelled = models.BooleanField("Отменено?", default=False)

    created_at = models.DateTimeField("Время создания бронирования", auto_now_add=True)
    updated_at = models.DateTimeField("Время последнего изменения бронирования", auto_now=True)

    receipt = None

    class Meta:
        # https://runebook.dev/ru/docs/django/ref/contrib/postgres/constraints
        # ctrl+f exclude_overlapping_reservations
        constraints = [
            ExclusionConstraint(
                name="exclude_reservations_overlapping",
                expressions=[
                    (
                        TsTzRange("check_in_datetime", "check_out_datetime", RangeBoundary()),
                        RangeOperators.OVERLAPS,
                    ),
                    ("house", RangeOperators.EQUAL),
                ],
                condition=Q(cancelled=False) | Q(house=None),
            ),
        ]

        verbose_name = "Бронь домика"
        verbose_name_plural = 'Брони домиков'

    def save(self, *args, **kwargs):
        # TODO из-за того, что оно (check_datetime_fields) находится здесь (до full_clean) в админке
        #  при создании неправильного бронирования вместо
        #  небольшой красной плашки вылетает желтая страница с ошибкой
        self.check_datetime_fields()
        # вызывать эту функцию выше следует именно до full_clean
        # Чтобы если она не проходит, возникала именно ValidationError, а не какая-то другая
        self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        self.clean_check_in_datetime()
        self.clean_check_out_datetime()
        self.clean_extra_persons_amount()

        # если все хорошо, то высчитать цену
        from houses.services.price_calculators import calculate_reservation_receipt
        if not self.price:
            self.receipt = calculate_reservation_receipt(house=self.house,
                                                         check_in_datetime=self.check_in_datetime,
                                                         check_out_datetime=self.check_out_datetime,
                                                         extra_persons_amount=self.extra_persons_amount, )
            self.price = self.receipt.total

    def clean_extra_persons_amount(self):
        if self.extra_persons_amount < 0:
            raise ValidationError("Невозможно заселить отрицательное количество человек в домик")
        if self.house.base_persons_amount + self.extra_persons_amount > self.house.max_persons_amount:
            raise ValidationError(f"Невозможно заселить столько человек в домик: \n"
                                  f"Базовое количество человек: {self.house.base_persons_amount}\n"
                                  f"Дополнительно количество человек: {self.extra_persons_amount}\n"
                                  f"Максимальное количество человек: {self.house.max_persons_amount}")

    def clean_check_in_datetime(self):
        if self.check_in_datetime.time() not in Pricing.ALLOWED_CHECK_IN_TIMES:
            raise ValidationError(f"Недопустимое время ВЪЕЗДА - {self.check_in_datetime}. "
                                  f"Доступное время - {Pricing.ALLOWED_CHECK_IN_TIMES.keys()}")

    def clean_check_out_datetime(self):
        if self.check_out_datetime.time() not in Pricing.ALLOWED_CHECK_OUT_TIMES:
            raise ValidationError(f"Недопустимое время ВЫЕЗДА - {self.check_out_datetime}. "
                                  f"Доступное время - {Pricing.ALLOWED_CHECK_OUT_TIMES.keys()}")

    def check_datetime_fields(self):
        if self.check_in_datetime.date() <= now().date():
            raise ValidationError("Невозможно забронировать домик на прошедшую дату")

        if self.check_in_datetime >= self.check_out_datetime:
            raise ValidationError("Дата и время заезда должны быть строго меньше даты и времени выезда")

    def __str__(self):
        if self.house:
            return f'{self.house.name} ({self.check_in_datetime.strftime("%d.%m %H:%M")})' \
                   f'-({self.check_out_datetime.strftime("%d.%m %H:%M")})'
        return f'{self.house} ({self.check_in_datetime.strftime("%d.%m %H:%M")})' \
               f'-({self.check_out_datetime.strftime("%d.%m %H:%M")})'
