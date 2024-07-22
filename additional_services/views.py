from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from core.mixins import ByActionMixin
from additional_services.models import AdditionalService
from additional_services.serializers import AdditionalServiceDetailSerializer


class AdditionalServiceViewSet(
    ByActionMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    serializer_classes_by_action = {
        "default": None,
        "list": AdditionalServiceDetailSerializer,
    }
    queryset = AdditionalService.objects.filter(active=True)
