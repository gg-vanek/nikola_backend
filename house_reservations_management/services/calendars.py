import logging
from datetime import date as Date, timedelta

from django.db.models import QuerySet
from django.utils.timezone import now

from house_reservations_billing.services.price_calculators import (
    calculate_house_price_by_day,
    is_holiday,
    calculate_extra_persons_price,
)
from house_reservations_management.services.reservations_overlapping import (
    filter_for_available_houses_by_day,
    filter_for_available_houses_by_period,
)
from houses.models import House

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


def _get_day_prices(
        total_persons_amount: int,
        day: Date,
        houses: QuerySet[House],
) -> dict:
    day_prices = {}
    for house in houses:
        day_prices[house] = calculate_house_price_by_day(house, day) \
                            + calculate_extra_persons_price(house, total_persons_amount)
    return day_prices


def calculate_check_out_calendar(
        houses: QuerySet[House],
        total_persons_amount: int,
        check_in_date: Date,
        year: int,
        month: int,
) -> dict:
    first_month_day = Date(year=year, month=month, day=1)
    end_day = _get_calendar_end_day(year, month)
    calendar = {}
    if first_month_day >= check_in_date:
        houses = filter_for_available_houses_by_period(houses, check_in_date, first_month_day)

    day = first_month_day

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
            houses = filter_for_available_houses_by_day(houses, day)
            day_prices = _get_day_prices(total_persons_amount, day, houses)

            if day_prices:
                calendar[day_str].update({
                    "price": min(day_prices.values()),
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
