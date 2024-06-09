import logging

from rest_framework import serializers

from houses.models import House, HouseFeature, HousePicture

logger = logging.getLogger(__name__)


class HousePictureListSerializer(serializers.ModelSerializer):
    picture = serializers.CharField(read_only=True, source='picture.url')
    width = serializers.IntegerField(read_only=True, source='picture.width')
    height = serializers.IntegerField(read_only=True, source='picture.height')

    class Meta:
        model = HousePicture
        fields = ('picture', 'width', 'height')


class HouseFeatureListSerializer(serializers.ModelSerializer):
    picture = serializers.CharField(read_only=True, source='picture.url')
    width = serializers.IntegerField(read_only=True, source='picture.width')
    height = serializers.IntegerField(read_only=True, source='picture.height')

    class Meta:
        model = HouseFeature
        fields = ('id', 'name', 'picture', 'width', 'height')


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
