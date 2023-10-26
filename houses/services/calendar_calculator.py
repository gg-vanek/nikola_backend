from datetime import datetime as Datetime, date as Date, timedelta

from django.db.models import QuerySet, Q, IntegerField, Value, Sum
from django.db.models.functions import Coalesce
from django.utils.timezone import now

from core.models import Pricing
from houses.models import HouseReservation, House
from houses.services.price_calculators import calculate_house_price_by_day
import logging

logger = logging.getLogger(__name__)


def calculate_calendar(houses: list[House] | QuerySet[House],
                       calendar_start_date: Date,
                       calendar_end_date: Date) -> dict[str: dict[str: int | None]]:
    calendar = {}
    day = calendar_start_date

    while day <= calendar_end_date:
        if day <= now().date():
            # не показываем цены домиков в уже прошедшие дни
            # все равно их нельзя забронировать :)
            calendar[day.strftime("%d-%m-%Y")] = {'price': None}
        else:
            minimum_day_price = None
            # если в этот день не будет свободных домиков, то цена так и останется None
            q = Q(
                reservations__check_in_datetime__lte=Datetime.combine(day, Pricing.ALLOWED_CHECK_IN_TIMES['default']),
                reservations__check_out_datetime__gte=Datetime.combine(day, Pricing.ALLOWED_CHECK_OUT_TIMES['default'])
            )
            for house in houses.annotate(
                    overlapping_reservations=Coalesce(
                        Sum("reservations", filter=q, distinct=True),
                        Value(0),
                        output_field=IntegerField()
                    )).filter(overlapping_reservations=0):
                # TODO дальнейшая оптимизация - .values("id", "base_price", "holidays_multiplier")
                house_day_price = calculate_house_price_by_day(house=house, day=day, use_cached_data=True)
                # обновляем минимальную цену
                if minimum_day_price:
                    minimum_day_price = min(minimum_day_price, house_day_price)
                else:
                    minimum_day_price = house_day_price

            calendar[day.strftime("%d-%m-%Y")] = {'price': minimum_day_price}
        day += timedelta(days=1)

    return calendar
