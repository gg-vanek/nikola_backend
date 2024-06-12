from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import RangeOperators, RangeBoundary
from django.db import models
from django.db.models import Q
from django.utils import timezone

from clients.models import Client
from core.generators import slug_generator
from house_reservations.sql_functions import TsTzRange
from house_reservations.validators import (
    check_datetime_fields,
    clean_check_in_datetime,
    clean_check_out_datetime,
    clean_total_persons_amount,
)


class HouseReservation(models.Model):
    slug = models.CharField(verbose_name="Строковый идентификатор", max_length=64, default=slug_generator)
    house = models.ForeignKey("houses.House", verbose_name="Домик", on_delete=models.SET_NULL,
                              null=True, related_name='reservations')
    client = models.ForeignKey(Client, verbose_name="Клиент", on_delete=models.SET_NULL,
                               null=True, related_name='reservations')

    check_in_datetime = models.DateTimeField("Дата и время заезда")
    check_out_datetime = models.DateTimeField("Дата и время выезда")
    total_persons_amount = models.IntegerField("Количество человек для проживания в домике")

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
        # Note: При обновлении бронирования через админку чек не обновится автоматически
        # Нужно будет зайти в админку чека и нажать в ней сохранить - тогда пересчитается

        # TODO из-за того, что оно (check_datetime_fields) находится здесь (до full_clean) - в админке
        #  при создании неправильного бронирования вместо
        #  небольшой красной плашки вылетает желтая страница с ошибкой
        check_datetime_fields(self.local_check_in_datetime, self.local_check_out_datetime)
        # вызывать эту функцию выше следует именно до full_clean
        # Чтобы если она не проходит, возникала именно ValidationError, а не какая-то другая
        self.full_clean()

        super().save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        clean_check_in_datetime(self.local_check_in_datetime)
        clean_check_out_datetime(self.local_check_out_datetime)
        clean_total_persons_amount(self.total_persons_amount, self.house)

    @property
    def local_check_in_datetime(self):
        return timezone.localtime(self.check_in_datetime)

    @property
    def local_check_out_datetime(self):
        return timezone.localtime(self.check_out_datetime)

    def __str__(self):
        return f"Бронирование {self.slug}"
