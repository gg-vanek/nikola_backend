import logging

from django.db.models import Q, QuerySet
from rest_framework.filters import BaseFilterBackend
from rest_framework.request import Request

logger = logging.getLogger(__name__)


class HousesMaxPersonsAmountFilter(BaseFilterBackend):
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
