from datetime import datetime as Datetime, date as Date

from django.db.models import QuerySet
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.mixins import ByActionMixin
from house_reservations_management.serializers.calendars_parameters import CalendarsParametersSerializer
from house_reservations_management.services.calendars import calculate_check_in_calendar, calculate_check_out_calendar
from houses.filters import FilterHousesByMaxPersonsAmount
from houses.models import House


class CalendarsViewSet(
    ByActionMixin,
    GenericViewSet,
):
    serializer_classes_by_action = {
        "default": None,
        "calendar": CalendarsParametersSerializer,
        "single_house_calendar": CalendarsParametersSerializer,
    }

    queryset = House.objects.filter(active=True)

    filter_backends = [
        FilterHousesByMaxPersonsAmount,
        # TODO HousesWithFeaturesFilter,
    ]

    def get_calendar(
            self,
            houses: QuerySet[House],
            year: int,
            month: int,
            total_persons_amount: int = 1,
            chosen_check_in_date: Date = None,
    ) -> dict:
        if chosen_check_in_date:
            return calculate_check_out_calendar(
                houses=houses,
                total_persons_amount=total_persons_amount,
                check_in_date=chosen_check_in_date,
                year=year,
                month=month,
            )
        else:
            return calculate_check_in_calendar(
                houses=houses,
                year=year,
                month=month,
            )

    @action(methods=['get'], url_path='calendar', detail=False)
    def calendar(self, request: Request, *args, **kwargs):
        calendar_parameters_serializer = self.get_serializer(data=request.query_params)
        calendar_parameters_serializer.is_valid(raise_exception=True)

        houses = self.filter_queryset(self.get_queryset())

        calendar_data = self.get_calendar(houses, **calendar_parameters_serializer.validated_data)
        return Response({"calendar": calendar_data})

    @action(methods=['get'], url_path='calendar', detail=True)
    def single_house_calendar(self, request: Request, *args, **kwargs):
        calendar_parameters_serializer = self.get_serializer(data=request.query_params)
        calendar_parameters_serializer.is_valid(raise_exception=True)

        house = self.queryset.filter(id=self.kwargs['pk'])

        calendar_data = self.get_calendar(house, **calendar_parameters_serializer.validated_data)
        return Response({"calendar": calendar_data})
