from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from core.mixins import ByActionMixin
from houses.models import House, HouseFeature
from houses.serializers import HouseFeatureListSerializer, HouseDetailSerializer


class HouseViewSet(
    ByActionMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    serializer_classes_by_action = {
        "default": None,
        "retrieve": HouseDetailSerializer,
    }
    queryset = House.objects.filter(active=True)


class HouseFeatureViewSet(
    ByActionMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    serializer_classes_by_action = {
        "default": None,
        "list": HouseFeatureListSerializer,
    }
    queryset = HouseFeature.objects.all()
