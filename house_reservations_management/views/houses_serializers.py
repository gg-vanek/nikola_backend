from rest_framework import serializers

from houses.models import House
from house_reservations_billing.services.price_calculators import light_calculate_reservation_price

from datetime import datetime as Datetime

import logging

from houses.serializers import HouseDetailSerializer

logger = logging.getLogger(__name__)


class HouseListWithTotalPriceSerializer(HouseDetailSerializer):
    # если нет дат в запросе - total_price == None
    # если в эти даты домик занят хотя бы в один из дней - total_price == None
    # в остальных случаях высчитывается суммарная цена проживания в домике в указанные даты

    total_price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = House
        fields = HouseDetailSerializer.Meta.fields + ["total_price"]

    def validate_query_params(self) -> tuple[Datetime, Datetime, int] | None:
        query_params = self.context["request"].query_params
        try:
            check_in_date = Datetime.strptime(query_params.get("check_in_date"), "%d-%m-%Y").date()
            check_out_date = Datetime.strptime(query_params.get("check_out_date"), "%d-%m-%Y").date()
        except (ValueError, TypeError):
            # если нет какой-то из дат - мы не можем высчитать суммарную цену бронирования
            logger.error("Invalid date format provided in query parameters")
            return None

        try:
            total_persons_amount = query_params.get("total_persons_amount", self.instance.base_persons_amount)
            total_persons_amount = int(total_persons_amount)
            total_persons_amount = max(total_persons_amount, self.instance.base_persons_amount)
        except (ValueError, TypeError):
            # если total_persons_amount не конвертируется в int -> не можем посчитать суммарную стоимость
            logger.error("Invalid total_persons_amount provided in query parameters")
            return None

        return check_in_date, check_out_date, total_persons_amount

    def get_total_price(self, house: House) -> int | None:
        validated_params = self.validate_query_params()
        if not validated_params:
            # если параметры не прошли валидацию, возвращаем None
            return None

        check_in_date, check_out_date, total_persons_amount = validated_params

        total_price = light_calculate_reservation_price(
            house=house,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            total_persons_amount=total_persons_amount,
        )

        return total_price