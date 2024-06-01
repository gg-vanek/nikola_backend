import logging

from rest_framework import serializers

from clients.serializers import ClientSerializer
from house_reservations.models import HouseReservation
from houses.serializers import HouseDetailSerializer

logger = logging.getLogger(__name__)


class HouseReservationSerializer(serializers.ModelSerializer):
    house = HouseDetailSerializer()
    client = ClientSerializer()

    class Meta:
        model = HouseReservation
        fields = [
            "slug",
            "house",
            "client",
            'check_in_datetime',
            'check_out_datetime',
            'total_persons_amount',
            'preferred_contact',
            'comment',
        ]
