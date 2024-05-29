from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from core.mixins import ByActionMixin
from house_reservations_management.views.houses_filters import HousesAvailableByDateFilter
from houses.filters import HousesMaxPersonsAmountFilter
from houses.models import House
from .houses_serializers import HouseListWithTotalPriceSerializer


class HouseViewSet(
    ByActionMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    serializer_classes_by_action = {
        "default": None,
        "list": HouseListWithTotalPriceSerializer,
    }

    queryset = House.objects.all()
    filter_backends = [
        HousesMaxPersonsAmountFilter,
        # TODO HousesWithFeaturesFilter,
        HousesAvailableByDateFilter
    ]
