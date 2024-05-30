from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.mixins import ByActionMixin
from core.models import Pricing
from house_reservations_billing.serializers import HouseReservationWithBillSerializer
from houses.models import House
from services import upsert_client
from .house_reservation_parameters_serializers import HouseReservationParametersSerializer
from ..services.create_house_reservation import create_reservation, calculate_reservation


class HouseReservationsManagementViewSet(ByActionMixin,
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
    @csrf_exempt
    def reservation_price(self, request: Request, *args, **kwargs):
        house = self.queryset.get(id=self.kwargs['pk'])

        reservation_parameters_serializer = self.get_serializer(house, data=request.data)
        reservation_parameters_serializer.is_valid(raise_exception=True)

        reservation = calculate_reservation(reservation_parameters_serializer.validated_data)

        try:
            reservation.clean()

            return Response({"reservation": HouseReservationWithBillSerializer(reservation).data},
                            status=status.HTTP_200_OK)
        # TODO обернуть ошибку нормально
        except ValidationError as e:
            return Response({"detail": str(e.messages)},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], url_path='new_reservation', detail=True)
    @csrf_exempt
    def new_reservation(self, request: Request, *args, **kwargs):
        house = self.queryset.get(id=self.kwargs['pk'])

        client = upsert_client(request.data)

        reservation_parameters_serializer = self.get_serializer(house, data=request.data)
        reservation_parameters_serializer.is_valid(raise_exception=True)

        try:
            reservation_data = reservation_parameters_serializer.validated_data
            preferred_contact = request.data["preferred_contact"]
            comment = request.data.get("comment", ' ')
            reservation_data.update({
                "client": client,
                "house": house,
                "preferred_contact": preferred_contact,
                "comment": comment
            })
        except KeyError:
            return Response({"error": "Поле preferred_contact не должно быть пустым"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            reservation = create_reservation(reservation_data)

            # TODO celery --- cancel if not approved payment
            # TODO telegram notification
            # TODO email notification (also via celery)

            return Response({"slug": reservation.slug}, status=status.HTTP_200_OK)
        # TODO обернуть ошибку нормально
        except ValidationError as e:
            return Response({"detail": str(e.messages)},
                            status=status.HTTP_400_BAD_REQUEST)
