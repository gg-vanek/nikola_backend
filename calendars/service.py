from datetime import date as Date, timedelta

import logging
from django.db.models import QuerySet
from django.utils.timezone import now

from houses.models import House
from house_reservations.services.check_overlapping import filter_for_available_houses_by_day, filter_for_available_houses_by_period
from billing.services.price_calculators import calculate_house_price_by_day, is_holiday

logger = logging.getLogger(__name__)


def calculate_check_in_calendar(houses: QuerySet[House],
                                year: int,
                                month: int) -> dict[str: dict[str: int | None]]:
    calendar = {}
    day = Date(year=year, month=month, day=1)
    end_day = Date(year=year + month // 12, month=month % 12 + 1, day=1)  # просто первый день следующего месяца

    while day < end_day:
        calendar[day.strftime("%d-%m-%Y")] = {}
        calendar[day.strftime("%d-%m-%Y")]["weekday"] = day.weekday()
        calendar[day.strftime("%d-%m-%Y")]["is_holiday"] = is_holiday(day)

        if day <= now().date():
            # не показываем цены домиков в уже прошедшие дни
            # все равно их нельзя забронировать :)
            calendar[day.strftime("%d-%m-%Y")]["check_in_is_available"] = False
            calendar[day.strftime("%d-%m-%Y")]["reason"] = "Passed day"

        else:
            # проверяем, можно ли въехать в рассматриваемый день, поэтому добавляем 1 день (см описание функции)
            available_houses = filter_for_available_houses_by_day(houses, day + timedelta(days=1))

            calendar[day.strftime("%d-%m-%Y")]["check_in_is_available"] = bool(available_houses)

        day += timedelta(days=1)

    return calendar


def calculate_check_out_calendar(houses: QuerySet[House],
                                 check_in_date: Date,
                                 year: int,
                                 month: int) -> dict[str: dict[str: int | None]]:
    calendar = {}
    day = Date(year=year, month=month, day=1)
    end_day = Date(year=year + month // 12, month=month % 12 + 1, day=1)  # просто первый день следующего месяца

    if day <= check_in_date:
        # случай когда мы идем по дням вперед и либо доходим до конца месяца, либо до первого дня бронирования
        accumulated_prices = {house: 0 for house in houses}
    else:
        # случай когда мы должны уже знать, сколько стоит бронирование каждого домика во все дни до этого суммарно
        # при этом нас интересуют только те домики которые имеют весь этот промежуток свободным
        houses = filter_for_available_houses_by_period(houses, check_in_date=check_in_date, check_out_date=day)

        accumulated_prices = {house: 0 for house in houses}

        # для множества домиков, свободных весь период от даты заезда до начала рассматриваемого месяца вычислим цену
        calendar_month_start = day
        day = check_in_date + timedelta(days=1)
        while day < calendar_month_start:
            for house in houses:
                # для каждого из домиков высчитать суммарную стоимость к первому дню текущего месяца
                accumulated_prices[house] += calculate_house_price_by_day(house, day)
                
            day += timedelta(days=1)
    # day == calendar_month_start снова

    while day < end_day:
        calendar[day.strftime("%d-%m-%Y")] = {}
        calendar[day.strftime("%d-%m-%Y")]["weekday"] = day.weekday()
        calendar[day.strftime("%d-%m-%Y")]["is_holiday"] = is_holiday(day)

        if day <= check_in_date:
            # не показываем цены домиков в дни, которые до дня въезда
            # все равно их нельзя забронировать :)
            calendar[day.strftime("%d-%m-%Y")]['price'] = None
            calendar[day.strftime("%d-%m-%Y")]['check_out_is_available'] = False
            calendar[day.strftime("%d-%m-%Y")]["reason(debug)"] = "Before_check_in"
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
                    calendar[day.strftime("%d-%m-%Y")]["reason(debug)"] = "No houses available for this check in and out"
                    day += timedelta(days=1)
            else:
                calendar[day.strftime("%d-%m-%Y")]['price'] = minimum_day_price
                calendar[day.strftime("%d-%m-%Y")]['check_out_is_available'] = True

        day += timedelta(days=1)

    return calendar
