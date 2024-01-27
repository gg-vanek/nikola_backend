from dataclasses import asdict
from datetime import datetime as Datetime

from django.utils.timezone import now
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from clients.models import Client
from clients.serializers import ClientSerializer
from core.mixins import ByActionMixin
from core.models import Pricing

from houses.filters import AvailableByDateHousesFilter, MaxPersonsAmountHousesFilter
from houses.models import House, HouseFeature, HouseReservation
from houses.serializers import HouseFeatureListSerializer, HouseListSerializer, HouseReservationParametersSerializer

from calendars.service import calculate_check_in_calendar, calculate_check_out_calendar

from houses.services.price_calculators import calculate_reservation_receipt


class HouseViewSet(ByActionMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    serializer_classes_by_action = {
        "default": None,
        "list": HouseListSerializer,
        "calendar": None,
        "reservation_price": HouseReservationParametersSerializer,
        "new_reservation": HouseReservationParametersSerializer,
    }
    queryset = House.objects.all()

    filter_backends = [
        MaxPersonsAmountHousesFilter,
        # FeaturesHousesFilter,
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
            month = int(self.request.query_params.get("month"))
            assert 1 <= month <= 12
            year = int(self.request.query_params.get("year"))
            assert now().year <= year
            return None
        except (TypeError, ValueError, AssertionError):
            return Response({"error": "month и year должны быть целыми положительными числами. "
                                      "Номер месяца не может быть меньше 1 или больше 12"},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], url_path='calendar', detail=False)
    def calendar(self, request: Request, *args, **kwargs):
        error_message_response = self.calendar_clean_and_check_request()
        if error_message_response:
            return error_message_response

        month = int(self.request.query_params.get("month"))
        year = int(self.request.query_params.get("year"))
        houses = self.filter_queryset(self.get_queryset())

        check_in_date = self.request.query_params.get("chosen_check_in_date")
        if check_in_date:
            check_in_date = Datetime.strptime(check_in_date, "%d-%m-%Y").date()
            return Response({"calendar": calculate_check_out_calendar(houses=houses,
                                                                      check_in_date=check_in_date,
                                                                      year=year,
                                                                      month=month)})
        return Response({"calendar": calculate_check_in_calendar(houses=houses,
                                                                  year=year,
                                                                  month=month)})

    @action(methods=['get'], url_path='calendar', detail=True)
    def single_house_calendar(self, request: Request, *args, **kwargs):
        error_message_response = self.calendar_clean_and_check_request()
        if error_message_response:
            return error_message_response

        month = int(self.request.query_params.get("month"))
        year = int(self.request.query_params.get("year"))

        house = self.queryset.filter(id=self.kwargs['pk'])

        check_in_date = self.request.query_params.get("check_in_date")
        if check_in_date:
            check_in_date = Datetime.strptime(check_in_date, "%d-%m-%Y").date()
            return Response({"calendar": calculate_check_out_calendar(houses=house,
                                                                      check_in_date=check_in_date,
                                                                      year=year,
                                                                      month=month)})

        return Response({"calendar": calculate_check_in_calendar(houses=house,
                                                                  year=year,
                                                                  month=month)})

    @action(methods=['get'], url_path='reservation_options', detail=True)
    def reservation_options(self, request: Request, *args, **kwargs):
        house = self.queryset.get(id=self.kwargs['pk'])

        return Response({
            "base_persons_amount": house.base_persons_amount,
            "max_persons_amount": house.max_persons_amount,
            "price_per_extra_person": house.price_per_extra_person,
            "check_in_times": Pricing.serializable_times_dict(d=Pricing.ALLOWED_CHECK_IN_TIMES),
            "check_out_times": Pricing.serializable_times_dict(d=Pricing.ALLOWED_CHECK_OUT_TIMES),
        }, status=status.HTTP_200_OK)

    @action(methods=['put'], url_path='reservation_price', detail=True)
    def reservation_price(self, request: Request, *args, **kwargs):
        house = self.queryset.get(id=self.kwargs['pk'])
        reservation_parameters_serializer = self.get_serializer(house, data=request.data)
        reservation_parameters_serializer.is_valid(raise_exception=True)
        receipt = calculate_reservation_receipt(house=house,
                                                **reservation_parameters_serializer.validated_data,
                                                use_cached_data=False)
        return Response({"receipt": asdict(receipt),
                         "total": receipt.total,
                         "house_id": self.kwargs['pk'],
                         **reservation_parameters_serializer.validated_data},
                        status=status.HTTP_200_OK)

    @action(methods=['post'], url_path='new_reservation', detail=True)
    def new_reservation(self, request: Request, *args, **kwargs):
        house = self.queryset.get(id=self.kwargs['pk'])

        client_serializer = ClientSerializer(data=request.data)
        client_serializer.is_valid(raise_exception=True)
        try:
            client = Client.objects.get(email=client_serializer.validated_data["email"])
            if client.first_name != client_serializer.validated_data["first_name"] or \
                    client.last_name != client_serializer.validated_data["last_name"]:
                pass  # TODO придумать что делать если у клиента та же почта, но другое имя
        except Client.DoesNotExist:
            client = client_serializer.create(client_serializer.validated_data)
            client.save()

        reservation_parameters_serializer = self.get_serializer(house, data=request.data)
        reservation_parameters_serializer.is_valid(raise_exception=True)

        try:
            preferred_contact = request.data["preferred_contact"]
            comment = request.data.get("comment", ' ')
        except KeyError:
            return Response({"error": "Поле preferred_contact не должно быть пустым"},
                            status=status.HTTP_400_BAD_REQUEST)

        reservation = HouseReservation.objects.create(client=client,
                                                      house=house,
                                                      preferred_contact=preferred_contact,
                                                      comment=comment,
                                                      **reservation_parameters_serializer.validated_data)
        receipt = reservation.receipt

        # TODO celery --- cancel if not approved payment
        # TODO telegram notification
        # TODO email notification (also via celery)

        return Response({"receipt": asdict(receipt),
                         "total": receipt.total,
                         "house_id": self.kwargs['pk'],
                         **reservation_parameters_serializer.validated_data,
                         "preferred_contact": preferred_contact,
                         "comment": comment},
                        status=status.HTTP_201_CREATED)


class HouseFeatureViewSet(ByActionMixin,
                          mixins.ListModelMixin,
                          GenericViewSet):
    serializer_classes_by_action = {
        "default": None,
        "list": HouseFeatureListSerializer,
    }
    queryset = HouseFeature.objects.all()
