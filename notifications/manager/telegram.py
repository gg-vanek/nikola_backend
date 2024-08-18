import logging

import telebot
from django.conf import settings

from house_reservations.models import HouseReservation
from notifications.manager.general import ManagerNotificationsBaseClass
from notifications.manager.templates import NEW_RESERVATION_CREATED

logger = logging.getLogger(__name__)


class ManagerNotificationsTelegram(ManagerNotificationsBaseClass):
    Bot: telebot.TeleBot
    chat_ids: list[int]

    def __init__(self, api_key: str, chat_ids: list[int]):
        self.Bot = telebot.TeleBot(
            token=api_key,
        )
        self.chat_ids=chat_ids

    def send_message_to_all_chats(self, message: str):
        for chat_id in self.chat_ids:
            self.Bot.send_message(chat_id, message)

    def new_reservation_created(self, reservation: HouseReservation):
        return self.send_message_to_all_chats(
            message=NEW_RESERVATION_CREATED.format(
                reservation_house_name=reservation.house.name,
                reservation_check_in_datetime=reservation.check_in_datetime.strftime("%d-%m %H:%M"),
                reservation_check_out_datetime=reservation.check_out_datetime.strftime("%d-%m %H:%M"),
                reservation_slug=reservation.slug,
                host=settings.ALLOWED_HOSTS[0],
                reservation_id=reservation.id,
                client_lastname=reservation.client.last_name,
                client_firstname=reservation.client.first_name,
                preferred_contact=reservation.preferred_contact,
                reservation_comment=reservation.comment,
            )
        )

    def there_are_some_unapproved_reservations(self, reservations: list[HouseReservation]):
        pass
