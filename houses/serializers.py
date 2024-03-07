from datetime import datetime as Datetime

import logging
from django.core.validators import MinValueValidator
from django.utils.timezone import now, get_default_timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from core.models import Pricing
from houses.models import House, HouseFeature, HousePicture
from houses.services.check_overlapping import check_if_house_free_by_period

from houses.services.price_calculators import calculate_reservation_receipt
from django.conf import settings

logger = logging.getLogger(__name__)


class HousePictureListSerializer(serializers.ModelSerializer):
    class Meta:
        model = HousePicture
        fields = ('picture',)


class HouseFeatureListSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseFeature
        fields = ('id', 'name', 'icon',)


class HouseDetailSerializer(serializers.ModelSerializer):
    pictures = HousePictureListSerializer(many=True)
    features = HouseFeatureListSerializer(many=True)

    class Meta:
        model = House
        fields = ('id', 'name',
                  'description', 'features', 'pictures',
                  'base_price',
                  'base_persons_amount',
                  'max_persons_amount',
                  'price_per_extra_person',)


class HouseListSerializer(serializers.ModelSerializer):
    # если нет дат в запросе - total_price == None
    # если в эти даты домик занят хотя бы в один из дней - total_price == None
    # в остальных случаях высчитывается суммарная цена проживания в домике в указанные даты

    total_price = serializers.SerializerMethodField(read_only=True)
    pictures = HousePictureListSerializer(many=True)
    features = HouseFeatureListSerializer(many=True)

    class Meta:
        model = House
        fields = ('id', 'name',
                  'description', 'features', 'pictures',
                  'base_price', 'total_price',
                  'base_persons_amount',
                  'max_persons_amount',
                  'price_per_extra_person',)

    def get_total_price(self, house: House) -> int | None:
        query_params = self.context["request"].query_params
        try:
            check_in_date = Datetime.strptime(query_params.get("check_in_date"), "%d-%m-%Y").date()
            check_out_date = Datetime.strptime(query_params.get("check_out_date"), "%d-%m-%Y").date()
        except (ValueError, TypeError):
            # если нет какой-то из дат - мы не можем высчитать суммарную цену бронирования
            return None

        try:
            total_persons_amount = query_params.get("total_persons_amount", house.base_persons_amount)
            total_persons_amount = int(total_persons_amount)
            total_persons_amount = max(total_persons_amount, house.base_persons_amount)
        except (ValueError, TypeError):
            # если total_persons_amount не конвертируется в int -> не можем посчитать суммарную стоимость
            return None

        # Весь коммент ниже - перестраховка. Сюда не должны прийти такие дома
        # Это перестраховка просто. Тут не должно оказаться такого домика
        # if total_persons_amount >= house.max_persons_amount:
        #     # с указанными параметрами фильтрации этот домик не удастся забронировать
        #     return None
        # Отсеять дома которые забронированы в один из интересующих
        # if HouseReservation.objects.filter(house=house, check_in_date__lt=day, check_out_datetime__gt=day):
        # return None

        extra_persons_amount = total_persons_amount - house.base_persons_amount
        check_in_datetime = Datetime.combine(
            check_in_date, Pricing.ALLOWED_CHECK_IN_TIMES['default'], tzinfo=get_default_timezone())
        check_out_datetime = Datetime.combine(
            check_out_date, Pricing.ALLOWED_CHECK_OUT_TIMES['default'], tzinfo=get_default_timezone())

        receipt = calculate_reservation_receipt(house=house,
                                                check_in_datetime=check_in_datetime,
                                                check_out_datetime=check_out_datetime,
                                                extra_persons_amount=extra_persons_amount)

        return receipt.nights_total


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
