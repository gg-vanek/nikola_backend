from datetime import date as Date, timedelta

import logging
from django.db.models import QuerySet
from django.utils.timezone import now

from houses.models import House
from .reservations_overlapping import (
    filter_for_available_houses_by_day,
    filter_for_available_houses_by_period,
)
from house_reservations_billing.services.price_calculators import (
    calculate_house_price_by_day,
    is_holiday,
)

logger = logging.getLogger(__name__)


# TODO опитимизировать количество запросов к бд - они летят на каждый день месяца

def calculate_check_in_calendar(
        houses: QuerySet[House],
        year: int,
        month: int,
) -> dict[str: dict[str: int | None]]:
    day = Date(year=year, month=month, day=1)
    end_day = Date(year=year + month // 12, month=month % 12 + 1, day=1)  # просто первый день следующего месяца

    calendar = {}

    while day < end_day:
        calendar[day.strftime("%d-%m-%Y")] = {}
        calendar[day.strftime("%d-%m-%Y")]["weekday"] = day.weekday()
        calendar[day.strftime("%d-%m-%Y")]["is_holiday"] = is_holiday(day)

        if day <= now().date():
            # не показываем цены домиков в уже прошедшие дни поскольку их нельзя забронировать.
            calendar[day.strftime("%d-%m-%Y")]["check_in_is_available"] = False
            calendar[day.strftime("%d-%m-%Y")]["reason (debug)"] = "Passed day"

        else:
            # проверяем, можно ли въехать в рассматриваемый день, поэтому добавляем 1 день
            available_houses = filter_for_available_houses_by_day(houses, day + timedelta(days=1))

            # если есть хоть один домик в который можно въехать - день доступен для въезда
            calendar[day.strftime("%d-%m-%Y")]["check_in_is_available"] = bool(available_houses)

        day += timedelta(days=1)

    return calendar


def calculate_check_out_calendar(
        houses: QuerySet[House],
        check_in_date: Date,
        year: int,
        month: int,
) -> dict[str: dict[str: int | None]]:
    day = Date(year=year, month=month, day=1)
    end_day = Date(year=year + month // 12, month=month % 12 + 1, day=1)  # просто первый день следующего месяца

    calendar = {}

    if day <= check_in_date:
        # Если первый день вычисляемого календаря находится до даты въезда, то
        # первый день с not-None ценой - день следующий за днем въезда
        # 1) если день въезда находится в следующем месяце - все дни рассматриваемого месяца имеют None цену
        # 2) если день въезда находится в рассматриваемом месяце - все дни до дня въезда включительно будут
        #    иметь None цену, а последующие до конца месяца - not-None цену
        # В любом случае - накопленная цена на домики "от дня въезда до текущего дня" равна нулю
        accumulated_prices = {house: 0 for house in houses}
    else:
        # Если день въезда расположен до первого дня вычисляемого календаря, то нам нужно выяснить,
        # какая цена накоплена у домиков за предыдущие месяцы (начиная со дня въезда)
        # При этом нас интересуют только те домики которые имеют весь промежуток от дня въезда до текущего дня свободным
        houses = filter_for_available_houses_by_period(houses, check_in_date=check_in_date, check_out_date=day)

        accumulated_prices = {house: 0 for house in houses}

        # Для множества домиков, свободных весь период от даты заезда до
        # начала рассматриваемого месяца вычислим цену на начало этого месяца
        calendar_month_start = day
        day = check_in_date + timedelta(days=1)
        while day < calendar_month_start:
            for house in houses:
                accumulated_prices[house] += calculate_house_price_by_day(house, day)

            day += timedelta(days=1)

    # На текущем шаге day == calendar_month_start

    while day < end_day:
        calendar[day.strftime("%d-%m-%Y")] = {}
        calendar[day.strftime("%d-%m-%Y")]["weekday"] = day.weekday()
        calendar[day.strftime("%d-%m-%Y")]["is_holiday"] = is_holiday(day)

        if day <= check_in_date:
            # не показываем цены домиков в дни, которые до дня въезда - бронирование с такими датами невозможно
            calendar[day.strftime("%d-%m-%Y")]['price'] = None
            calendar[day.strftime("%d-%m-%Y")]['check_out_is_available'] = False
            calendar[day.strftime("%d-%m-%Y")]["reason (debug)"] = "Check-out should be after check-in"
        else:
            # если в этот день не будет свободных домиков, то цена так и останется None
            minimum_day_price = None

            available_houses = filter_for_available_houses_by_day(houses, day)
            houses = available_houses

            for house in list(accumulated_prices.keys()):
                if house not in houses:
                    del accumulated_prices[house]

            for house in houses:
                accumulated_prices[house] += calculate_house_price_by_day(house=house, day=day)
                house_day_price = accumulated_prices[house]

                # обновляем минимальную цену
                if minimum_day_price:
                    minimum_day_price = min(minimum_day_price, house_day_price)
                else:
                    minimum_day_price = house_day_price

            if minimum_day_price is None:
                # этот день и все дни после него помечаем как None
                while day < end_day:
                    calendar[day.strftime("%d-%m-%Y")] = {}
                    calendar[day.strftime("%d-%m-%Y")]["weekday"] = day.weekday()
                    calendar[day.strftime("%d-%m-%Y")]["is_holiday"] = is_holiday(day)
                    calendar[day.strftime("%d-%m-%Y")]['price'] = None
                    calendar[day.strftime("%d-%m-%Y")]['check_out_is_available'] = False
                    calendar[day.strftime("%d-%m-%Y")][
                        "reason (debug)"] = "No houses available for this check in and out"
                    day += timedelta(days=1)
            else:
                calendar[day.strftime("%d-%m-%Y")]['price'] = minimum_day_price
                calendar[day.strftime("%d-%m-%Y")]['check_out_is_available'] = True

        day += timedelta(days=1)

    return calendar
