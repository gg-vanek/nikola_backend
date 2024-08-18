from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from clients.serializers import ClientSerializer
from clients.services import upsert_client
from core.mixins import ByActionMixin
from core.models import Pricing
from house_reservations_billing.serializers import HouseReservationWithBillSerializer
from house_reservations_management.serializers.house_reservation_parameters import HouseReservationParametersSerializer, \
    AdditionalReservationParametersSerializer
from house_reservations_management.services.house_reservation import create_reservation, calculate_reservation
from house_reservations_management.tasks import new_reservation_created_manager_notification, \
    new_reservation_created_user_notification
from houses.models import House


class HouseReservationsManagementViewSet(ByActionMixin,
                                         mixins.RetrieveModelMixin,
                                         mixins.ListModelMixin,
                                         GenericViewSet):
    serializer_classes_by_action = {
        "default": None,
        "reservation_price": HouseReservationParametersSerializer,
        "new_reservation": HouseReservationParametersSerializer,
    }
    queryset = House.objects.filter(active=True)

    @action(methods=['get'], url_path='reservations/options', detail=True)
    def reservation_options(self, request: Request, *args, **kwargs):
        house = self.queryset.get(id=self.kwargs['pk'])

        return Response({
            "base_persons_amount": house.base_persons_amount,
            "max_persons_amount": house.max_persons_amount,
            "price_per_extra_person": house.price_per_extra_person,
            "check_in_times": Pricing.serializable_times_dict(d=Pricing.ALLOWED_CHECK_IN_TIMES),
            "check_out_times": Pricing.serializable_times_dict(d=Pricing.ALLOWED_CHECK_OUT_TIMES),
        }, status=status.HTTP_200_OK)

    @action(methods=['put'], url_path='reservations/price', detail=True)
    def reservation_price(self, request: Request, *args, **kwargs):
        reservation_parameters_serializer = self.get_serializer(
            data={
                "house": self.kwargs['pk'],
                **request.data,
            },
        )
        reservation_parameters_serializer.is_valid(raise_exception=True)

        reservation = calculate_reservation(reservation_parameters_serializer.validated_data)
        reservation.clean()

        return Response({"reservation": HouseReservationWithBillSerializer(reservation).data},
                        status=status.HTTP_200_OK)

    @action(methods=['post'], url_path='reservations', detail=True)
    def new_reservation(self, request: Request, *args, **kwargs):
        client_serializer = ClientSerializer(data=request.data)
        client_serializer.is_valid(raise_exception=True)
        client = upsert_client(client_serializer)

        reservation_parameters_serializer = self.get_serializer(
            data={
                "house": self.kwargs['pk'],
                **request.data,
            },
        )
        reservation_parameters_serializer.is_valid(raise_exception=True)

        additional_reservation_parameters_serializer = AdditionalReservationParametersSerializer(data=request.data)
        additional_reservation_parameters_serializer.is_valid(raise_exception=True)

        reservation = create_reservation({
            **reservation_parameters_serializer.validated_data,
            **additional_reservation_parameters_serializer.validated_data,
            **{"client": client},
        })

        # TODO celery - cancel if not approved payment
        new_reservation_created_manager_notification.delay(reservation.pk)
        new_reservation_created_user_notification.delay(reservation.pk)

        return Response({"slug": reservation.slug}, status=status.HTTP_200_OK)
