import logging

from rest_framework import serializers

from additional_services.models import AdditionalService, AdditionalServicePicture

logger = logging.getLogger(__name__)


class AdditionalServicePictureListSerializer(serializers.ModelSerializer):
    picture = serializers.CharField(read_only=True, source='picture.url')
    width = serializers.IntegerField(read_only=True, source='picture.width')
    height = serializers.IntegerField(read_only=True, source='picture.height')

    class Meta:
        model = AdditionalServicePicture
        fields = ('picture', 'width', 'height')


class AdditionalServiceDetailSerializer(serializers.ModelSerializer):
    pictures = AdditionalServicePictureListSerializer(many=True)

    class Meta:
        model = AdditionalService
        fields = [
            'id',
            'name',
            'description',
            'pictures',
            'price_string',
            'telegram_contact_link',
        ]
