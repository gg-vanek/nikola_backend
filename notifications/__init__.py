import os

from notifications.manager.telegram import ManagerNotificationsTelegram
from notifications.user.email import UserNotificationsEmail
from notifications.user.email_templates.new_reservation.template_builder import NewReservationTemplateBuilder

ManagerNotificationsService = ManagerNotificationsTelegram(
    api_key=os.getenv(
        "TELEGRAM_API_KEY",
        "7472374239:AAFXbVugGpCHbe13p-F4BNjO0brOsXLCOJc",
    ),
    chat_ids=list(
        map(
            int,
            os.getenv(
                "TELEGRAM_MANAGER_CHATS",
                "409733921",
            ).split(","),
        )
    ),
)
UserNotificationService = UserNotificationsEmail(
    email_login=os.getenv("EMAIL_LOGIN", ""),
    email_password=os.getenv("EMAIL_PASSWORD", ""),
    new_reservation_template_builder=NewReservationTemplateBuilder(),
)
