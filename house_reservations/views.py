from django.core.exceptions import ValidationError
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from clients.models import Client
from clients.serializers import ClientSerializer
from core.mixins import ByActionMixin
from core.models import Pricing
from house_reservations.models import HouseReservation
from house_reservations.serializers import HouseReservationParametersSerializer, HouseReservationSerializer

from houses.models import House


class HouseReservationsViewSet(ByActionMixin,
                               mixins.RetrieveModelMixin,
                               mixins.ListModelMixin,
                               GenericViewSet):
    serializer_classes_by_action = {
        "default": None,
        "reservation_price": HouseReservationParametersSerializer,
        "new_reservation": HouseReservationParametersSerializer,
    }
    queryset = House.objects.all()

    @action(methods=['get'], url_path='options', detail=True)
    def reservation_options(self, request: Request, *args, **kwargs):
        house = self.queryset.get(id=self.kwargs['pk'])

        return Response({
            "base_persons_amount": house.base_persons_amount,
            "max_persons_amount": house.max_persons_amount,
            "price_per_extra_person": house.price_per_extra_person,
            "check_in_times": Pricing.serializable_times_dict(d=Pricing.ALLOWED_CHECK_IN_TIMES),
            "check_out_times": Pricing.serializable_times_dict(d=Pricing.ALLOWED_CHECK_OUT_TIMES),
        }, status=status.HTTP_200_OK)

    @action(methods=['put'], url_path='price', detail=True)
    def reservation_price(self, request: Request, *args, **kwargs):
        # TODO добавить проверку доступности бронирования
        house = self.queryset.get(id=self.kwargs['pk'])

        reservation_parameters_serializer = self.get_serializer(house, data=request.data)
        reservation_parameters_serializer.is_valid(raise_exception=True)

        reservation = HouseReservation(house=house,
                                       **reservation_parameters_serializer.validated_data)
        try:
            reservation.clean()

            return Response({"reservation": HouseReservationSerializer(reservation).data},
                            status=status.HTTP_200_OK)
        # TODO обернуть ошибку нормально
        except ValidationError as e:
            return Response({"detail": str(e.messages)},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], url_path='new_reservation', detail=True)
    def new_reservation(self, request: Request, *args, **kwargs):
        house = self.queryset.get(id=self.kwargs['pk'])

        client_serializer = ClientSerializer(data=request.data)
        client_serializer.is_valid(raise_exception=True)
        try:
            client = Client.objects.get(email=client_serializer.validated_data["email"])  # TODO get_or_create
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

        try:
            reservation = HouseReservation.objects.create(client=client,
                                                          house=house,
                                                          preferred_contact=preferred_contact,
                                                          comment=comment,
                                                          **reservation_parameters_serializer.validated_data)

            # TODO celery --- cancel if not approved payment
            # TODO telegram notification
            # TODO email notification (also via celery)

            return Response({"reservation": HouseReservationSerializer(reservation).data},
                            status=status.HTTP_200_OK)
        # TODO обернуть ошибку нормально
        except ValidationError as e:
            return Response({"detail": str(e.messages)},
                            status=status.HTTP_400_BAD_REQUEST)

