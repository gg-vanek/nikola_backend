import logging

from rest_framework import serializers

from house_reservations.models import HouseReservation
from house_reservations.serializers import HouseReservationSerializer
from .models import HouseReservationBill

logger = logging.getLogger(__name__)


class HouseReservationBillSerializer(serializers.ModelSerializer):
    promo_code = serializers.SerializerMethodField()

    class Meta:
        model = HouseReservationBill
        fields = (
            'total',
            'chronological_positions',
            'non_chronological_positions',
            "promo_code",
        )

    def get_promo_code(self, bill):
        if bill.promo_code:
            return bill.promo_code.code


class HouseReservationWithBillSerializer(HouseReservationSerializer):
    bill = HouseReservationBillSerializer()

    class Meta:
        model = HouseReservation
        fields = HouseReservationSerializer.Meta.fields + ["bill", ]
