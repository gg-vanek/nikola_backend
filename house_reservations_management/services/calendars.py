from datetime import date as Date, timedelta
import logging
from django.db.models import QuerySet
from django.utils.timezone import now
from houses.models import House
from house_reservations_management.services.reservations_overlapping import (
    filter_for_available_houses_by_day,
    filter_for_available_houses_by_period,
)
from house_reservations_billing.services.price_calculators import (
    calculate_house_price_by_day,
    is_holiday,
    calculate_extra_persons_price,
)

logger = logging.getLogger(__name__)


def _get_calendar_end_day(year: int, month: int) -> Date:
    return Date(year=year + month // 12, month=month % 12 + 1, day=1)


def _create_day_entry(day: Date) -> dict:
    return {
        "weekday": day.weekday(),
        "is_holiday": is_holiday(day),
    }


def calculate_check_in_calendar(
        houses: QuerySet[House],
        year: int,
        month: int,
) -> dict:
    day = Date(year=year, month=month, day=1)
    end_day = _get_calendar_end_day(year, month)
    calendar = {}

    while day < end_day:
        day_str = day.strftime("%d-%m-%Y")
        calendar[day_str] = _create_day_entry(day)

        if day <= now().date():
            # не показываем цены домиков в уже прошедшие дни поскольку их нельзя забронировать.
            calendar[day_str].update({
                "check_in_is_available": False,
                "reason (debug)": "Passed day"
            })
        else:
            # проверяем, можно ли въехать в рассматриваемый день, поэтому добавляем 1 день
            available_houses = filter_for_available_houses_by_day(houses, day + timedelta(days=1))
            # если есть хоть один домик в который можно въехать - день доступен для въезда
            calendar[day_str]["check_in_is_available"] = bool(available_houses)

        day += timedelta(days=1)

    return calendar


def _get_initial_accumulated_prices(
        houses: QuerySet[House],
        total_persons_amount: int,
        day: Date,
        check_in_date: Date,
) -> dict:
    accumulated_prices = {house: 0 for house in houses}
    if day <= check_in_date:
        # Если первый день вычисляемого календаря находится до даты въезда, то
        # первый день с not-None ценой - день следующий за днем въезда
        # 1) если день въезда находится в следующем месяце - все дни рассматриваемого месяца имеют None цену
        # 2) если день въезда находится в рассматриваемом месяце - все дни до дня въезда включительно будут
        #    иметь None цену, а последующие до конца месяца - not-None цену
        # В любом случае - накопленная цена на домики "от дня въезда до текущего дня" равна нулю
        return accumulated_prices

    # Если день въезда расположен до первого дня вычисляемого календаря, то нам нужно выяснить,
    # какая цена накоплена у домиков за предыдущие месяцы (начиная со дня въезда)
    # При этом нас интересуют только те домики которые имеют весь промежуток от дня въезда до текущего дня свободным
    houses = filter_for_available_houses_by_period(houses, check_in_date, day)
    day_iter = check_in_date + timedelta(days=1)

    # Для множества домиков, свободных весь период от даты заезда до
    # начала рассматриваемого месяца вычислим цену на начало этого месяца
    while day_iter < day:
        for house in houses:
            accumulated_prices[house] += calculate_house_price_by_day(house, day_iter) \
                                         + calculate_extra_persons_price(house, total_persons_amount)
        day_iter += timedelta(days=1)

    return accumulated_prices


def _update_accumulated_prices(
        accumulated_prices: dict,
        total_persons_amount: int,
        day: Date,
        houses: QuerySet[House],
) -> dict:
    available_houses = filter_for_available_houses_by_day(houses, day)
    for house in list(accumulated_prices.keys()):
        if house not in available_houses:
            del accumulated_prices[house]
        else:
            accumulated_prices[house] += calculate_house_price_by_day(house, day) \
                                         + calculate_extra_persons_price(house, total_persons_amount)
    return accumulated_prices


def calculate_check_out_calendar(
        houses: QuerySet[House],
        total_persons_amount: int,
        check_in_date: Date,
        year: int,
        month: int,
) -> dict:
    day = Date(year=year, month=month, day=1)
    end_day = _get_calendar_end_day(year, month)
    calendar = {}
    accumulated_prices = _get_initial_accumulated_prices(houses, total_persons_amount, day, check_in_date)

    while day < end_day:
        day_str = day.strftime("%d-%m-%Y")
        calendar[day_str] = _create_day_entry(day)

        if day <= check_in_date:
            calendar[day_str].update({
                "price": None,
                "check_out_is_available": False,
                "reason (debug)": "Check-out should be after check-in",
            })
        else:
            accumulated_prices = _update_accumulated_prices(accumulated_prices, total_persons_amount, day, houses)
            day_prices = list(accumulated_prices.values())
            if day_prices:
                calendar[day_str].update({
                    "price": min(day_prices),
                    "check_out_is_available": True,
                })
            else:
                calendar[day_str].update({
                    "price": None,
                    "check_out_is_available": False,
                    "reason (debug)": "No houses available for this check in and out",
                })

        day += timedelta(days=1)

    return calendar
