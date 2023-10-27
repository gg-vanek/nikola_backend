from django.db.models import Q, QuerySet, IntegerField, Sum, Value, F
from django.db.models.functions import Coalesce
from django.utils.timezone import now
from rest_framework.filters import BaseFilterBackend
from datetime import datetime as Datetime

from rest_framework.request import Request

from core.models import Pricing
import logging

logger = logging.getLogger(__name__)


class MaxPersonsAmountHousesFilter(BaseFilterBackend):
    def filter_queryset(self, request: Request, queryset: QuerySet, view):
        query_params = request.query_params
        query = Q()

        try:
            total_persons_amount = query_params.get("total_persons_amount")
            total_persons_amount = int(total_persons_amount)
            query &= Q(max_persons_amount__gte=total_persons_amount)
        except (ValueError, TypeError):
            query = Q()

        return queryset.filter(query)


class FeaturesHousesFilter(BaseFilterBackend):
    def filter_queryset(self, request: Request, queryset: QuerySet, view):
        query_params = request.query_params
        needed_features = query_params.get("features", None)
        query = Q()

        if needed_features and isinstance(needed_features, str):
            try:
                needed_features = list(map(int, needed_features.split(',')))
                for n_f in needed_features:
                    query &= Q(features=n_f)
            except ValueError:
                query = Q()

        return queryset.filter(query)


class AvailableByDateHousesFilter(BaseFilterBackend):
    def filter_queryset(self, request: Request, queryset: QuerySet, view):
        query_params = request.query_params
        query = Q()
        try:
            check_in_date = Datetime.strptime(query_params.get("check_in_date"),
                                              "%d-%m-%Y").date()
            check_out_date = Datetime.strptime(query_params.get("check_out_date"),
                                               "%d-%m-%Y").date()

            if not (now().date() < check_in_date < check_out_date):
                # если прилетели неправильные даты check_in и check_out или
                # если пытаются забронировать что-то на прошедшую дату
                raise ValueError

            check_in_datetime = Datetime.combine(check_in_date, Pricing.ALLOWED_CHECK_IN_TIMES['default'])
            check_out_datetime = Datetime.combine(check_out_date, Pricing.ALLOWED_CHECK_OUT_TIMES['default'])

            q1 = Q(reservations__check_out_datetime__lt=check_in_datetime, reservations__canceled=False)
            q2 = Q(reservations__check_in_datetime__gt=check_out_datetime, reservations__canceled=False)
            # два условия выше - условия, что очередное бронирование не пересекается с выбранными датами
            # нам нужно выбрать те домики, для которых суммарное количество таких бронирований
            # не равно общему количеству бронирований

            # TODO есть queryset.extra позволяющий делать запуск raw SQL
            queryset = queryset.annotate(
                booked_before=Coalesce(
                    Sum("reservations", filter=Q(q1), distinct=True),
                    Value(0),
                    output_field=IntegerField()
                ),
                booked_after=Coalesce(
                    Sum("reservations", filter=Q(q2), distinct=True),
                    Value(0),
                    output_field=IntegerField()
                ),
                booked_total=Coalesce(
                    Sum("reservations", distinct=True),
                    Value(0),
                    output_field=IntegerField()
                ),
                overlapping_reservations=F("booked_total") - F("booked_before") - F("booked_after")
            ).filter(overlapping_reservations=0)

        except (ValueError, TypeError):
            # если нет какой-то из дат - мы не можем фильтровать
            # также если проблема с порядком дат "now < in < out" попадаем сюда же
            query = Q()

        return queryset
