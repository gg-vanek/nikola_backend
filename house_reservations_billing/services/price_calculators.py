import logging
from datetime import time as Time, date as Date, datetime as Datetime, timedelta

from core.functions import is_holiday
from events.models import Event
from house_reservations.validators import clean_total_persons_amount, check_datetime_fields
from houses.models import House

logger = logging.getLogger(__name__)


def light_calculate_reservation_price(
        house: House,
        check_in_date: Date,
        check_out_date: Date,
        total_persons_amount: int,
) -> int:
    # Проверки корректности входных данных
    clean_total_persons_amount(total_persons_amount, house)
    check_datetime_fields(
        Datetime.combine(check_in_date, Time()),
        Datetime.combine(check_out_date, Time()),
    )

    total_price = 0

    # NOTE: ночь идет перед днем
    # иными словами множитель выходного дня применяется к ночам пт-сб и сб-вс, но не к вс-пн
    date = check_in_date + timedelta(days=1)
    while date <= check_out_date:
        total_price += calculate_house_price_by_day(house, date) \
                       + calculate_extra_persons_price(house, total_persons_amount)
        date = date + timedelta(days=1)

    return total_price


def calculate_house_price_by_day(
        house: House,
        day: Date,
) -> int:
    price = house.base_price
    # TODO events нужно доставать из кэша, потому что их мало
    events = Event.objects.filter(start_date__lte=day, end_date__gte=day)

    if is_holiday(day):
        price *= house.holidays_multiplier

    for event in events:
        price *= event.multiplier

    price = int(round(price, -2))

    return price


def calculate_extra_persons_price(
        house: House,
        total_persons_amount: int,
) -> int:
    extra_persons_amount = max(0, total_persons_amount - house.base_persons_amount)

    return extra_persons_amount * house.price_per_extra_person
