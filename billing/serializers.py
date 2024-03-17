from rest_framework import serializers

import logging

logger = logging.getLogger(__name__)


class HouseReservationBillSerializer(serializers.ModelSerializer):
    # TODO
    class Meta:
        fields = ('id',
                  'total',
                  'nights',
                  'extra_services')
