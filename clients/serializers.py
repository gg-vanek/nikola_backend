from rest_framework import serializers
from clients.models import Client
from core.validators import name_validator


class ClientSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(validators=[name_validator], max_length=150)
    last_name = serializers.CharField(validators=[name_validator], max_length=150)

    class Meta:
        model = Client
        fields = ("email", "first_name", "last_name")
