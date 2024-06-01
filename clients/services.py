import logging

from clients.models import Client

logger = logging.getLogger(__name__)


def upsert_client(client_serializer) -> Client:
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
