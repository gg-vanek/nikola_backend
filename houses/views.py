from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.mixins import ByActionMixin
from houses.filters import AvailableByDateHousesFilter, MaxPersonsAmountHousesFilter, FeaturesHousesFilter

from houses.models import House, HouseFeature
from houses.serializers import HouseFeatureListSerializer, HouseListSerializer


class HouseViewSet(ByActionMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   GenericViewSet):
    serializer_classes_by_action = {
        "default": None,
        "list": HouseListSerializer,
        "retrieve": None,
    }
    queryset = House.objects.all()

    filter_backends = [
        MaxPersonsAmountHousesFilter,
        FeaturesHousesFilter,
        AvailableByDateHousesFilter,
    ]


class HouseFeatureViewSet(ByActionMixin,
                          mixins.ListModelMixin,
                          GenericViewSet):
    serializer_classes_by_action = {
        "default": None,
        "list": HouseFeatureListSerializer,
    }
    queryset = HouseFeature.objects.all()
