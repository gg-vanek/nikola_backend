import calendar
from datetime import date as Date, timedelta

import logging

from core.errors import LogicError, IncorrectPeopleAmountInReservationException, \
    IncorrectDatetimesException
from events.models import Event
from houses.models import House

logger = logging.getLogger(__name__)


def light_calculate_reservation_price(house: House | int,
                                      check_in_date: Date, check_out_date: Date,
                                      total_persons_amount: int) -> int:
    if isinstance(house, int):
        try:
            house = House.objects.get(pk=house)
        except House.DoesNotExist as e:
            raise LogicError(f"Некорректный id домика = {house}") from e

    if not (house.base_persons_amount <= total_persons_amount <= house.max_persons_amount):
        raise IncorrectPeopleAmountInReservationException("Некорректное значение total_persons_amount - "
                                                          "это должно быть целое число в промежутке от "
                                                          f"количества проживающих в домике по умолчанию ({house.base_persons_amount} чел.) "
                                                          f"до максимально допустимого количества проживающих "
                                                          f"в домике ({house.max_persons_amount} чел.)")
    if check_in_date >= check_out_date:
        raise IncorrectDatetimesException(
            f"Некорректные даты въезда и выезда (въезд позже выезда): {check_in_date.strftime('%d-%m-%Y')} >= {check_out_date.strftime('%d-%m-%Y')}")

    extra_persons_amount = total_persons_amount - house.base_persons_amount

    total_price = 0

    # NOTE: ночь идет перед днем
    # иными словами множитель выходного дня применяется к ночам пт-сб и сб-вс, но не к вс-пн
    date = check_in_date + timedelta(days=1)
    while date <= check_out_date:
        total_price += calculate_house_price_by_day(house, date) + extra_persons_amount * house.price_per_extra_person
        date = date + timedelta(days=1)

    return total_price


def calculate_house_price_by_day(house: House, day: Date) -> int:
    # TODO в этой функции нужно принимать не house, а house_id, base_price, holidays_multiplier

    price = house.base_price
    # TODO events нужно доставать из кэша, потому что их мало
    events = Event.objects.filter(start_date__lte=day, end_date__gte=day)

    if is_holiday(day):
        price *= house.holidays_multiplier

    for event in events:
        price *= event.multiplier

    price = int(round(price, -2))

    return price


def is_holiday(day: Date) -> bool:
    # код ниже очень долго работает. Никто не будет 15 секунд ждать календарь

    # cached_day = cache.get(day)
    # if cached_day:
    #     return cached_day
    #
    # # logger.error(requests.get("https://isdayoff.ru/"+day.strftime("%Y-%m-%d")).text)
    # is_holiday_flag = bool(int(requests.get("https://isdayoff.ru/"+day.strftime("%Y-%m-%d")).text))
    #
    # cache.set(day, is_holiday_flag, timeout=60*60*12)  # раз в 12 часов будет эта инфа обновляться
    #
    # return is_holiday_flag

    KNOWN_HOLIDAYS = [  # HARDCODE
        *[(i, 1) for i in range(1, 9)],
        (23, 2),
        (8, 3),
        (29, 4),
        (30, 4),
        (1, 5),
        (9, 5), (10, 5),
        (12, 6),
        (4, 11), (30, 12), (31, 12),
    ]

    return day.weekday() in [calendar.SATURDAY, calendar.SUNDAY] or ((day.day, day.month) in KNOWN_HOLIDAYS)
