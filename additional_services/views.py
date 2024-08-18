from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from additional_services.models import AdditionalService
from additional_services.serializers import AdditionalServiceDetailSerializer
from core.mixins import ByActionMixin


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
