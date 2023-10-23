import os

import logging
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import RangeOperators, RangeBoundary, DateTimeRangeField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

from django.db import models
from django.db.models import Func, Q
from django.utils.timezone import now

from core.models import Pricing

from clients.models import Client

logger = logging.getLogger(__name__)


class TsTzRange(Func):
    function = "TSTZRANGE"
    output_field = DateTimeRangeField()


def generate_house_picture_filename(instance, filename):
    path = os.path.join('houses', 'pictures', str(instance.house.id), filename)
    return path


def generate_house_feature_icon_filename(instance, filename: str):
    path = os.path.join('houses_features', 'icons', str(instance.name) + '.' + filename.split('.')[-1])
    return path


class House(models.Model):
    name = models.CharField("Название домика", max_length=255, unique=True)

    description = models.TextField("Описание домика")
    features = models.ManyToManyField("HouseFeature", verbose_name="Плюшки", related_name='houses')

    base_price = models.IntegerField(
        "Базовая цена",
        default=10000,
        validators=[
            MinValueValidator(Pricing.MIN_HOUSE_BASE_PRICE,
                              message=f"Базовая цена домика должна быть не меньше, "
                                      f"чем {Pricing.MIN_HOUSE_BASE_PRICE}"), ])
    holidays_multiplier = models.FloatField(
        "Множитель в выходные и праздники",
        default=2,
        validators=[
            MinValueValidator(Pricing.MIN_HOUSE_HOLIDAYS_MULTIPLIER,
                              message=f"Множитель в выходные дни должен быть не меньше, "
                                      f"чем {Pricing.MIN_HOUSE_HOLIDAYS_MULTIPLIER}"),
        ])

    base_persons_amount = models.IntegerField("Базовое количество человек для проживания в домике", default=2)
    max_persons_amount = models.IntegerField("Максимальное количество человек для проживания в домике", default=3)
    price_per_extra_person = models.IntegerField("Цена за дополнительного человека", default=2000)

    created_at = models.DateTimeField("Время создания домика", auto_now_add=True)
    updated_at = models.DateTimeField("Время последнего изменения домика", auto_now=True)

    class Meta:
        verbose_name = "Домик"
        verbose_name_plural = 'Домики'

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class HousePicture(models.Model):
    house = models.ForeignKey(House, verbose_name="Домик",
                              on_delete=models.SET_NULL,
                              null=True, related_name='pictures')
    picture = models.ImageField("Путь до файла с изображением",
                                upload_to=generate_house_picture_filename)

    class Meta:
        verbose_name = "Изображение домика"
        verbose_name_plural = 'Изображения домиков'

    def __str__(self):
        return self.picture.name


class HouseFeature(models.Model):
    name = models.CharField("Название", max_length=127, unique=True)
    icon = models.ImageField("Иконка", upload_to=generate_house_feature_icon_filename)

    class Meta:
        verbose_name = "Фича домика"
        verbose_name_plural = 'Фичи домиков'

    def __str__(self):
        return self.name


class HouseReservation(models.Model):
    house = models.ForeignKey(House, verbose_name="Домик", on_delete=models.SET_NULL,
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
        from houses.services.price_calculators import calculate_reservation_price
        if not self.price:
            self.price = calculate_reservation_price(house=self.house,
                                                     check_in_datetime=self.check_in_datetime,
                                                     check_out_datetime=self.check_out_datetime,
                                                     extra_persons_amount=self.extra_persons_amount,
                                                     )

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
        return f'{self.house.name} ({self.check_in_datetime.strftime("%d.%m %H:%M")})' \
                                f'-({self.check_out_datetime.strftime("%d.%m %H:%M")})'
