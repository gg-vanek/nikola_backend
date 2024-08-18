from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from core.mixins import ByActionMixin
from house_reservations_management.filters.houses import HousesAvailableByDateFilter
from house_reservations_management.serializers.houses import HouseListWithTotalPriceSerializer
from houses.filters import FilterHousesByMaxPersonsAmount
from houses.models import House


class HouseListingViewSet(
    ByActionMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    serializer_classes_by_action = {
        "default": None,
        "list": HouseListWithTotalPriceSerializer,
    }

    queryset = House.objects.filter(active=True)
    filter_backends = [
        FilterHousesByMaxPersonsAmount,
        # TODO HousesWithFeaturesFilter,
        HousesAvailableByDateFilter
    ]
