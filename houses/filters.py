import logging
from datetime import datetime as Datetime
from django.db.models import Q, QuerySet, IntegerField, Sum, Value, F
from django.db.models.functions import Coalesce
from django.utils.timezone import now
from rest_framework.filters import BaseFilterBackend

from rest_framework.request import Request

from core.models import Pricing
from houses.services.check_overlapping import filter_for_available_houses_by_period

logger = logging.getLogger(__name__)


class MaxPersonsAmountHousesFilter(BaseFilterBackend):
    def filter_queryset(self, request: Request, queryset: QuerySet, view):
        query_params = request.query_params
        query = Q()

        try:
            max_persons_amount = query_params.get("max_persons_amount")
            max_persons_amount = int(max_persons_amount)
            query &= Q(max_persons_amount__gte=max_persons_amount)
        except (ValueError, TypeError):
            query = Q()

        return queryset.filter(query)


class AvailableByDateHousesFilter(BaseFilterBackend):
    def filter_queryset(self, request: Request, queryset: QuerySet, view):
        query_params = request.query_params
        try:
            check_in_date = Datetime.strptime(query_params.get("check_in_date"), "%d-%m-%Y").date()
            check_out_date = Datetime.strptime(query_params.get("check_out_date"), "%d-%m-%Y").date()

            if not now().date() < check_in_date < check_out_date:
                # если прилетели неправильные даты check_in и check_out или
                # если пытаются забронировать что-то на прошедшую дату
                raise ValueError

            check_in_datetime = Datetime.combine(check_in_date, Pricing.ALLOWED_CHECK_IN_TIMES['default'])
            check_out_datetime = Datetime.combine(check_out_date, Pricing.ALLOWED_CHECK_OUT_TIMES['default'])

            queryset = filter_for_available_houses_by_period(queryset, check_in_datetime, check_out_datetime)

        except (ValueError, TypeError):
            # если нет какой-то из дат - мы не можем фильтровать
            # также если проблема с порядком дат "now < in < out" попадаем сюда же
            pass

        return queryset
