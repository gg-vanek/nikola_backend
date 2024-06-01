from datetime import datetime as Datetime

from django.db.models import QuerySet
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.mixins import ByActionMixin
from house_reservations_management.serializers.calendars_parameters import CalendarsParametersSerializer
from house_reservations_management.services.calendars import calculate_check_in_calendar, calculate_check_out_calendar
from houses.filters import HousesMaxPersonsAmountFilter
from houses.models import House


class CalendarsViewSet(
    ByActionMixin,
    GenericViewSet,
):
    serializer_classes_by_action = {
        "default": None,
        "calendar": CalendarsParametersSerializer,
    }

    queryset = House.objects.all()

    filter_backends = [
        HousesMaxPersonsAmountFilter,
        # TODO HousesWithFeaturesFilter,
    ]

    def get_calendar(self, houses: QuerySet[House], year: int, month: int, check_in_date: str | None) -> dict:
        if check_in_date:
            check_in_date = Datetime.strptime(check_in_date, "%d-%m-%Y").date()
            return calculate_check_out_calendar(houses=houses, check_in_date=check_in_date, year=year, month=month)
        else:
            return calculate_check_in_calendar(houses=houses, year=year, month=month)

    @action(methods=['get'], url_path='calendar', detail=False)
    def calendar(self, request: Request, *args, **kwargs):
        calendar_parameters_serializer = self.get_serializer(data=request.query_params)
        calendar_parameters_serializer.is_valid(raise_exception=True)

        month = calendar_parameters_serializer.validated_data["month"]
        year = calendar_parameters_serializer.validated_data["year"]
        check_in_date = calendar_parameters_serializer.validated_data.get("chosen_check_in_date")

        houses = self.filter_queryset(self.get_queryset())

        calendar_data = self.get_calendar(houses, year, month, check_in_date)
        return Response({"calendar": calendar_data})

    @action(methods=['get'], url_path='calendar', detail=True)
    def single_house_calendar(self, request: Request, *args, **kwargs):
        calendar_parameters_serializer = self.get_serializer(data=request.query_params)
        calendar_parameters_serializer.is_valid(raise_exception=True)

        month = calendar_parameters_serializer.validated_data["month"]
        year = calendar_parameters_serializer.validated_data["year"]
        check_in_date = calendar_parameters_serializer.validated_data.get("chosen_check_in_date")

        house = self.queryset.filter(id=self.kwargs['pk'])

        calendar_data = self.get_calendar(house, year, month, check_in_date)
        return Response({"calendar": calendar_data})