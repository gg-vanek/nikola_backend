from django.utils.timezone import get_default_timezone

from rest_framework import serializers

from core.models import Pricing
from houses.models import House, HouseFeature, HousePicture
from houses.services.price_calculators import calculate_reservation_receipt

from datetime import datetime as Datetime

import logging

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
