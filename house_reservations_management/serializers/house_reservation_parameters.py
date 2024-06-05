import logging

from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import Pricing
from house_reservations_billing.models.promocode import HouseReservationPromoCode
from house_reservations_management.services.reservations_overlapping import check_if_house_free_by_period
from houses.models import House

logger = logging.getLogger(__name__)


class HouseReservationParametersSerializer(serializers.Serializer):
    house = serializers.PrimaryKeyRelatedField(queryset=House.objects.all(), required=True)
    check_in_datetime = serializers.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS,
                                                  format="%d-%m-%Y %H:%M", required=True)
    check_out_datetime = serializers.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS,
                                                   format="%d-%m-%Y %H:%M", required=True)
    total_persons_amount = serializers.IntegerField(validators=[
        MinValueValidator(0, message="В бронировании нельзя указывать отрицательное количество человек"),
    ], required=True)
    promo_code = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'house',
            'check_in_datetime',
            'check_out_datetime',
            'total_persons_amount',
            'promo_code',
        )

    def get_promo_code(self) -> HouseReservationPromoCode | None:
        requested_promo_code = self.initial_data.get("promo_code")
        promo_code = None
        if requested_promo_code:
            try:
                promo_code = HouseReservationPromoCode.objects.get(code=requested_promo_code)
            except HouseReservationPromoCode.DoesNotExist:
                raise ValidationError(f'Промокод "{requested_promo_code}" не найден')

        return promo_code

    def validate(self, attrs):
        house = attrs["house"]

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

        total_persons_amount = attrs["total_persons_amount"]
        if not (1 <= total_persons_amount <= house.max_persons_amount):
            raise ValidationError("Некорректное значение total_persons_amount - "
                                  "это должно быть целое число в промежутке от "
                                  f"одного (1 чел.) "
                                  f"до максимально допустимого количества проживающих "
                                  f"в домике ({house.max_persons_amount} чел.)")

        attrs["promo_code"] = self.get_promo_code()
        return attrs


class AdditionalReservationParametersSerializer(serializers.Serializer):
    preferred_contact = serializers.CharField(required=True)
    comment = serializers.CharField(required=False, allow_blank=True)
