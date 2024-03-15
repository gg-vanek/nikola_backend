from django.core.validators import MinValueValidator
from django.utils.timezone import now
from django.conf import settings

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import Pricing
from house_reservations.services.check_overlapping import check_if_house_free_by_period

import logging

logger = logging.getLogger(__name__)


class HouseReservationParametersSerializer(serializers.Serializer):
    check_in_datetime = serializers.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS,
                                                  format="%d-%m-%Y %H:%M", required=True)
    check_out_datetime = serializers.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS,
                                                   format="%d-%m-%Y %H:%M", required=True)
    extra_persons_amount = serializers.IntegerField(validators=[
        MinValueValidator(0, message="В бронировании нельзя указывать отрицательное количество человек"),
    ], required=True)

    class Meta:
        fields = ('id',
                  'check_in_datetime',
                  'check_out_datetime',
                  'extra_persons_amount',
                  )

    def validate(self, attrs):
        house = self.instance

        check_in_datetime = attrs["check_in_datetime"]
        check_out_datetime = attrs["check_out_datetime"]

        if check_in_datetime >= check_out_datetime:
            raise ValidationError("Дата заезда должна быть меньше даты выезда")
        if now().date() >= check_in_datetime.date():
            raise ValidationError("Дата заезда должна быть больше сегодняшней даты")
        if check_in_datetime.time() not in Pricing.ALLOWED_CHECK_IN_TIMES:
            raise ValidationError("Некорректное время въезда")
        if check_out_datetime.time() not in Pricing.ALLOWED_CHECK_OUT_TIMES:
            raise ValidationError("Некорректное время выезда")

        if check_if_house_free_by_period(house, check_in_datetime, check_out_datetime):
            raise ValidationError("Выбранное время бронирования недоступно. "
                                  "Попробуйте поставить другое время заезда/выезда, "
                                  "если дни заезда и выезда в календаре отмечены, как свободные.", )

        try:
            extra_persons_amount = attrs["extra_persons_amount"]
            assert extra_persons_amount >= 0
        except (ValueError, AssertionError) as e:
            raise ValidationError("Некорректное extra_persons_amount - "
                                  "это должно быть целое неотрицательное число") from e
        except KeyError as e:
            raise ValidationError("Отсутствует extra_persons_amount") from e

        return attrs
