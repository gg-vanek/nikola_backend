from django.core.validators import MinValueValidator
from django.utils.timezone import now
from django.conf import settings

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from billing.models import HouseReservationPromoCode
from billing.serializers import HouseReservationBillSerializer
from clients.serializers import ClientSerializer
from core.models import Pricing
from house_reservations.models import HouseReservation
from house_reservations.services.check_overlapping import check_if_house_free_by_period

import logging

from houses.serializers import HouseDetailSerializer

logger = logging.getLogger(__name__)


class HouseReservationSerializer(serializers.ModelSerializer):
    house = HouseDetailSerializer()
    client = ClientSerializer()
    bill = HouseReservationBillSerializer()

    class Meta:
        model = HouseReservation
        fields = (
            "house", "client", "bill",
            'check_in_datetime', 'check_out_datetime',
            'total_persons_amount',
            'preferred_contact',
            'comment',
        )


class HouseReservationParametersSerializer(serializers.Serializer):
    check_in_datetime = serializers.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS,
                                                  format="%d-%m-%Y %H:%M", required=True)
    check_out_datetime = serializers.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS,
                                                   format="%d-%m-%Y %H:%M", required=True)
    total_persons_amount = serializers.IntegerField(validators=[
        MinValueValidator(0, message="В бронировании нельзя указывать отрицательное количество человек"),
    ], required=True)
    promo_code = serializers.SerializerMethodField()

    class Meta:
        fields = ('id',
                  'check_in_datetime',
                  'check_out_datetime',
                  'total_persons_amount',
                  'promo_code',
                  )

    def get_promo_code(self) -> HouseReservationPromoCode | None:
        requested_promo_code = self.context["request"].data.get("promo_code")
        promo_code = None
        if requested_promo_code:
            try:
                promo_code = HouseReservationPromoCode.objects.get(code=requested_promo_code)
            except HouseReservationPromoCode.DoesNotExist as e:
                raise ValidationError(f'Промокод "{requested_promo_code}" не найден') from e

        return promo_code

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
            total_persons_amount = int(attrs["total_persons_amount"])
            assert house.base_persons_amount <= total_persons_amount <= house.max_persons_amount
        except (ValueError, AssertionError) as e:
            raise ValidationError("Некорректное значение total_persons_amount - "
                                  "это должно быть целое число в промежутке от "
                                  f"количества проживающих в домике по умолчанию ({house.base_persons_amount} чел.) "
                                  f"до максимально допустимого количества проживающих "
                                  f"в домике ({house.max_persons_amount} чел.)") from e
        except KeyError as e:
            raise ValidationError("Отсутствует total_persons_amount") from e

        # TODO тут написано криво, нужно переписать
        self.promo_code = self.get_promo_code()
        attrs["promo_code"] = self.promo_code

        return attrs
