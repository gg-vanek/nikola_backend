import logging

from models import Client
from serializers import ClientSerializer

logger = logging.getLogger(__name__)


def upsert_client(data) -> Client:
    client_serializer = ClientSerializer(data=data)
    client_serializer.is_valid(raise_exception=True)

    try:
        client = Client.objects.get(email=client_serializer.validated_data["email"])
        if client.first_name != client_serializer.validated_data["first_name"]:
            logger.info(
                f"Updated client with id {client.id}. "
                f"first_name: {client.first_name} -> {client_serializer.validated_data['first_name']}",
            )
            client.first_name = client_serializer.validated_data['first_name']
        if client.last_name != client_serializer.validated_data["last_name"]:
            logger.info(
                f"Updated client with id {client.id}. "
                f"last_name: {client.last_name} -> {client_serializer.validated_data['last_name']}",
            )
            client.last_name = client_serializer.validated_data['last_name']

    except Client.DoesNotExist:
        client = client_serializer.create(client_serializer.validated_data)

    client.save()
    return client
