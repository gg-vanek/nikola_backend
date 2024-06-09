import logging

from rest_framework import serializers

from houses.models import House, HouseFeature, HousePicture

logger = logging.getLogger(__name__)


class HousePictureListSerializer(serializers.ModelSerializer):
    picture = serializers.CharField(read_only=True, source='icon.url')

    class Meta:
        model = HousePicture
        fields = ('picture',)


class HouseFeatureListSerializer(serializers.ModelSerializer):
    icon = serializers.CharField(read_only=True, source='icon.url')

    class Meta:
        model = HouseFeature
        fields = ('id', 'name', 'icon',)


class HouseDetailSerializer(serializers.ModelSerializer):
    pictures = HousePictureListSerializer(many=True)
    features = HouseFeatureListSerializer(many=True)

    class Meta:
        model = House
        fields = [
            'id',
            'name',
            'description',
            'features',
            'pictures',
            'base_price',
            'base_persons_amount',
            'max_persons_amount',
            'price_per_extra_person',
        ]
