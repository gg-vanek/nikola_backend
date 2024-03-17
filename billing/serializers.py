from rest_framework import serializers

from billing.models import HouseReservationBill

import logging

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
