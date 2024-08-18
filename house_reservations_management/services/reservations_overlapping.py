import logging
from datetime import datetime as Datetime, date as Date, timedelta

from django.db.models import QuerySet, Q, IntegerField, Value, Sum, Count, F
from django.db.models.functions import Coalesce
from django.utils.timezone import get_default_timezone

from core.models import Pricing
from houses.models import House

logger = logging.getLogger(__name__)


def filter_for_available_houses_by_day(houses: QuerySet[House], day: Date) -> QuerySet[House]:
    """
    Эта функция получает на вход QuerySet из домиков (houses) и день выезда (day).

    Возвращает те домики, которые возможно забронировать на одну ночь, с выездом в переданный день (day)
    """
    # Это фильтр, который возвращает все бронирования для некоторого домика, которые имеют пересечение с промежутком
    # с Datetime.combine(day - timedelta(days=1), Pricing.ALLOWED_CHECK_IN_TIMES['latest'])
    # по Datetime.combine(day, Pricing.ALLOWED_CHECK_OUT_TIMES['earliest'])
    # проверяем отсутствие пересечения с latest check_in и earliest check_out, потому что это тот кейс
    # который необходим для свободности домика в рассматриваемую ночь
    q = Q(
        reservations__check_in_datetime__lte=Datetime.combine(
            day - timedelta(days=1),
            Pricing.ALLOWED_CHECK_IN_TIMES['latest'],
            tzinfo=get_default_timezone(),
        ),
        reservations__check_out_datetime__gte=Datetime.combine(
            day,
            Pricing.ALLOWED_CHECK_OUT_TIMES['earliest'],
            tzinfo=get_default_timezone(),
        ),
        reservations__cancelled=False,
    )

    # в коде ниже мы применяем для каждого домика фильтр составленный выше и считаем количество полученных бронирований
    # если оно равно нулю, то домик в рассматриваемую ночь свободен - поэтому производится фильтрация по этому полю
    available_houses = houses.annotate(
        overlapping_reservations=Coalesce(
            Sum("reservations", filter=q, distinct=True),
            Value(0),
            output_field=IntegerField()
        ),
    ).filter(overlapping_reservations=0)
    # TODO дальнейшая оптимизация - .values("id", "base_price", "holidays_multiplier")
    #  или глянуть какой запрос летит в бд и кидать его самому

    return available_houses


def filter_for_available_houses_by_period(
        houses: QuerySet[House],
        check_in_date: Date,
        check_out_date: Date,
) -> QuerySet[House]:
    booked_before_query = Q(
        reservations__check_out_datetime__lt=Datetime.combine(
            check_in_date,
            Pricing.ALLOWED_CHECK_IN_TIMES['latest'],
            tzinfo=get_default_timezone(),
        ),
        reservations__cancelled=False,
    )
    booked_after_query = Q(
        reservations__check_in_datetime__gt=Datetime.combine(
            check_out_date,
            Pricing.ALLOWED_CHECK_OUT_TIMES['earliest'],
            tzinfo=get_default_timezone(),
        ),
        reservations__cancelled=False,
    )
    # два условия выше - условия, что очередное бронирование не пересекается с выбранными датами
    # нам нужно выбрать те домики, для которых суммарное количество таких бронирований
    # не равно общему количеству бронирований
    booked_total_query = Q(reservations__cancelled=False)

    # есть еще queryset.extra позволяющий делать запуск raw SQL
    return houses.annotate(
        booked_before=Coalesce(
            Sum("reservations", filter=Q(booked_before_query), distinct=True),
            Value(0),
            output_field=IntegerField()
        ),
        booked_after=Coalesce(
            Sum("reservations", filter=Q(booked_after_query), distinct=True),
            Value(0),
            output_field=IntegerField()
        ),
        booked_total=Coalesce(
            Sum("reservations", filter=Q(booked_total_query), distinct=True),
            Value(0),
            output_field=IntegerField()
        ),
        overlapping_reservations=F("booked_total") - F("booked_before") - F("booked_after")
    ).filter(overlapping_reservations=0)


def check_if_house_free_by_period(house: House, check_in_datetime: Datetime, check_out_datetime: Datetime) -> bool:
    q1 = Q(check_out_datetime__lt=check_in_datetime, cancelled=False)
    q2 = Q(check_in_datetime__gt=check_out_datetime, cancelled=False)
    q3 = Q(cancelled=False)

    return house.reservations.annotate(
        booked_before=Coalesce(
            Count("id", filter=Q(q1), distinct=True),
            Value(0),
            output_field=IntegerField()
        ),
        booked_after=Coalesce(
            Count("id", filter=Q(q2), distinct=True),
            Value(0),
            output_field=IntegerField()
        ),
        booked_total=Coalesce(
            Count("id", filter=Q(q3), distinct=True),
            Value(0),
            output_field=IntegerField()
        ),
        overlapping_reservations=F("booked_total") - F("booked_before") - F("booked_after")
    ).exclude(overlapping_reservations=0).exists()

# Пример как можно было бы писать через сырой SQL запрос
#
# def check_if_house_free_by_period(house: House, check_in_datetime: Datetime, check_out_datetime: Datetime) -> bool:
#     sql_query = """
#     SELECT 1 FROM house_reservations_housereservation
#     WHERE house_id = %s AND cancelled = FALSE AND
#           (
#               check_in_datetime < %s AND check_out_datetime > %s
#           )
#     LIMIT 1
#     """
#     with connection.cursor() as cursor:
#         cursor.execute(sql_query, [house.id, check_out_datetime, check_in_datetime])
#         overlapping_reservations = cursor.fetchone()
#
#     return overlapping_reservations is None
