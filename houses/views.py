from datetime import datetime as Datetime
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.mixins import ByActionMixin
from houses.filters import AvailableByDateHousesFilter, MaxPersonsAmountHousesFilter, FeaturesHousesFilter

from houses.models import House, HouseFeature
from houses.serializers import HouseFeatureListSerializer, HouseListSerializer
from houses.services.calendar_calculator import calculate_calendar


class HouseViewSet(ByActionMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    serializer_classes_by_action = {
        "default": None,
        "list": HouseListSerializer,
        "calendar": None,
    }
    queryset = House.objects.all()

    filter_backends = [
        MaxPersonsAmountHousesFilter,
        FeaturesHousesFilter,
        AvailableByDateHousesFilter,
    ]

    def calendar_clean_and_check_request(self) -> Response | None:
        """Данный метод
        1) удаляет у request объекта некоторые фильтры, чтобы не применялся AvailableByDateHousesFilter
        2) проверяет корректность параметров календаря и возвращает Response если находит ошибку
        """

        # если тут была фильтрация по датам в которые домик свободен,
        # то эту фильтрацию нужно убрать
        _mutable = self.request.query_params._mutable
        self.request.query_params._mutable = True
        self.request.query_params["check_in_date"] = None
        self.request.query_params["check_out_date"] = None
        self.request.query_params._mutable = _mutable

        try:
            calendar_start_date = Datetime.strptime(self.request.query_params.get("calendar_start_date"),
                                                    "%d-%m-%Y").date()
            calendar_end_date = Datetime.strptime(self.request.query_params.get("calendar_end_date"),
                                                  "%d-%m-%Y").date()
        except (TypeError, ValueError):
            return Response({"detail": "Некорректное значение одной из дат. "
                                       "Значение должно соответствовать шаблону %d-%m-%Y"},
                            status=status.HTTP_400_BAD_REQUEST)

        if calendar_end_date < calendar_start_date:
            return Response({"detail": "calendar_end_date должна быть больше, чем calendar_start_date"},
                            status=status.HTTP_400_BAD_REQUEST)

        return None

    @action(methods=['get'], url_path='calendar', detail=False)
    def calendar(self, request: Request, *args, **kwargs):
        check = self.calendar_clean_and_check_request()
        if check:
            return check

        calendar_start_date = Datetime.strptime(self.request.query_params.get("calendar_start_date"), "%d-%m-%Y").date()
        calendar_end_date = Datetime.strptime(self.request.query_params.get("calendar_end_date"), "%d-%m-%Y").date()

        houses = self.filter_queryset(self.get_queryset())

        return Response({"calendar": calculate_calendar(houses=houses,
                                                        calendar_start_date=calendar_start_date,
                                                        calendar_end_date=calendar_end_date)})

    @action(methods=['get'], url_path='calendar', detail=True)
    def single_house_calendar(self, request: Request, *args, **kwargs):
        check = self.calendar_clean_and_check_request()
        if check:
            return check

        calendar_start_date = Datetime.strptime(self.request.query_params.get("calendar_start_date"), "%d-%m-%Y").date()
        calendar_end_date = Datetime.strptime(self.request.query_params.get("calendar_end_date"), "%d-%m-%Y").date()

        house = self.filter_queryset(self.get_queryset()).filter(id=self.kwargs['pk'])

        return Response({"calendar": calculate_calendar(houses=house,
                                                        calendar_start_date=calendar_start_date,
                                                        calendar_end_date=calendar_end_date)})


class HouseFeatureViewSet(ByActionMixin,
                          mixins.ListModelMixin,
                          GenericViewSet):
    serializer_classes_by_action = {
        "default": None,
        "list": HouseFeatureListSerializer,
    }
    queryset = HouseFeature.objects.all()
