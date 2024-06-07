import logging

from django.db.models import Q, QuerySet
from rest_framework.filters import BaseFilterBackend
from rest_framework.request import Request

logger = logging.getLogger(__name__)


class FilterHousesByMaxPersonsAmount(BaseFilterBackend):
    def filter_queryset(self, request: Request, queryset: QuerySet, view):
        query_params = request.query_params
        query = Q()

        try:
            requested_persons_amount = query_params.get("total_persons_amount")
            requested_persons_amount = int(requested_persons_amount)
            query &= Q(max_persons_amount__gte=requested_persons_amount)
        except (ValueError, TypeError):
            query = Q()

        return queryset.filter(query)
