from datetime import date as Date, timedelta

import logging
from django.core.exceptions import ValidationError

from core.models import Pricing

logger = logging.getLogger(__name__)


def calculate_reservation_price(reservation) -> int:
    price = 0

    check_in_datetime = reservation.check_in_datetime
    check_in_date = check_in_datetime.date()
    check_in_time = check_in_datetime.time()

    check_out_datetime = reservation.check_out_datetime
    check_out_date = check_out_datetime.date()
    check_out_time = check_out_datetime.time()

    # рассчитаем увеличение стоимости за счет раннего въезда или позднего выезда
    if check_in_time not in Pricing.ALLOWED_CHECK_IN_TIMES:
        logger.critical(f"Недопустимое время ВЪЕЗДА у бронирования {reservation.id} - {check_in_time}")
        raise ValidationError("Недопустимое время ВЪЕЗДА")
    if check_out_time not in Pricing.ALLOWED_CHECK_OUT_TIMES:
        logger.critical(f"Недопустимое время ВЫЕЗДА у бронирования {reservation.id} - {check_out_time}")
        raise ValidationError("Недопустимое время ВЫЕЗДА")

    # увеличение стоимости за ранний въезд
    price += \
        Pricing.ALLOWED_CHECK_IN_TIMES[check_in_time] \
        * calculate_house_price_by_day(reservation.house, check_in_date)

    # увеличение стоимости за поздний выезд
    price += \
        Pricing.ALLOWED_CHECK_OUT_TIMES[check_out_time] \
        * calculate_house_price_by_day(reservation.house, check_out_date)

    date = check_in_date
    while date < check_out_date:
        price += calculate_house_price_by_day(reservation.house, date)
        date = date + timedelta(days=1)

    return int(price)


def calculate_house_price_by_day(house, day: Date) -> int:
    price = house.base_price

    if is_holiday(day):
        price *= house.holidays_multiplier

    return int(price)


def is_holiday(day: Date):
    return day.weekday() in [5, 6]
