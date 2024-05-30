from datetime import datetime as Datetime

from django.db.models import QuerySet
from django.utils.timezone import now
from house_reservations_management.services.calendars import calculate_check_in_calendar, calculate_check_out_calendar
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.mixins import ByActionMixin
from houses.filters import HousesMaxPersonsAmountFilter
from houses.models import House


class CalendarsViewSet(
    ByActionMixin,
    GenericViewSet,
):
    serializer_classes_by_action = {
        "default": None,
        "calendar": None,
    }

    queryset = House.objects.all()

    filter_backends = [
        HousesMaxPersonsAmountFilter,
        # TODO HousesWithFeaturesFilter,
    ]

    @staticmethod
    def get_month_and_year(request: Request) -> tuple[int, int] | Response:
        try:
            month = int(request.query_params.get("month"))
            assert 1 <= month <= 12
            year = int(request.query_params.get("year"))
            assert now().year <= year
            return month, year
        except (TypeError, ValueError, AssertionError):
            return Response(
                {
                    "error": (
                        "month и year должны быть целыми положительными числами. "
                        "Номер месяца не может быть меньше 1 или больше 12. "
                        "Номер года не может быть меньше текущего года"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    def get_calendar(self, houses: QuerySet[House], year: int, month: int, check_in_date: str | None) -> dict:
        if check_in_date:
            check_in_date = Datetime.strptime(check_in_date, "%d-%m-%Y").date()
            return calculate_check_out_calendar(houses=houses, check_in_date=check_in_date, year=year, month=month)
        else:
            return calculate_check_in_calendar(houses=houses, year=year, month=month)

    @action(methods=['get'], url_path='calendar', detail=False)
    def calendar(self, request: Request, *args, **kwargs):
        month_and_year_parsed = self.get_month_and_year(request)
        if isinstance(month_and_year_parsed, Response):
            return month_and_year_parsed

        month, year = month_and_year_parsed
        houses = self.filter_queryset(self.get_queryset())
        check_in_date = request.query_params.get("chosen_check_in_date")

        calendar_data = self.get_calendar(houses, year, month, check_in_date)
        return Response({"calendar": calendar_data})

    @action(methods=['get'], url_path='calendar', detail=True)
    def single_house_calendar(self, request: Request, *args, **kwargs):
        month_and_year_parsed = self.get_month_and_year(request)
        if isinstance(month_and_year_parsed, Response):
            return month_and_year_parsed

        month, year = month_and_year_parsed
        house = self.queryset.filter(id=self.kwargs['pk'])
        check_in_date = request.query_params.get("chosen_check_in_date")

        calendar_data = self.get_calendar(house, year, month, check_in_date)
        return Response({"calendar": calendar_data})