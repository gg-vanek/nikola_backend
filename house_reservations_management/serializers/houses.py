import logging
from datetime import datetime as Datetime

from rest_framework import serializers

from house_reservations_billing.services.price_calculators import light_calculate_reservation_price, \
    calculate_extra_persons_price
from houses.models import House
from houses.serializers import HouseDetailSerializer

logger = logging.getLogger(__name__)


class HouseListWithTotalPriceSerializer(HouseDetailSerializer):
    # если нет дат в запросе - total_price == None
    # если в эти даты домик занят хотя бы в один из дней - total_price == None
    # в остальных случаях высчитывается суммарная цена проживания в домике в указанные даты

    total_price = serializers.SerializerMethodField(read_only=True)
    price_per_day = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = House
        fields = HouseDetailSerializer.Meta.fields + ["total_price", "price_per_day"]

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

        total_price = light_calculate_reservation_price(
            house=house,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            total_persons_amount=total_persons_amount,
        )

        return total_price

    def get_price_per_day(self, house: House) -> int | None:
        query_params = self.context["request"].query_params

        try:
            total_persons_amount = query_params.get("total_persons_amount", house.base_persons_amount)
            total_persons_amount = int(total_persons_amount)
            total_persons_amount = max(total_persons_amount, house.base_persons_amount)
        except (ValueError, TypeError):
            return house.base_price

        return house.base_price + calculate_extra_persons_price(house, total_persons_amount)
