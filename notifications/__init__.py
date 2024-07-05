import os

from notifications.manager.telegram import ManagerNotificationsTelegram
from notifications.user.email import UserNotificationsEmail

ManagerNotificationsService = ManagerNotificationsTelegram(
    os.getenv(
        "TELEGRAM_API_KEY",
        "7472374239:AAFXbVugGpCHbe13p-F4BNjO0brOsXLCOJc",
    ),
    chat_ids=list(
        map(
            int,
            os.getenv(
                "TELEGRAM_API_KEY",
                "7472374239:AAFXbVugGpCHbe13p-F4BNjO0brOsXLCOJc",
            ).split(","),
        )
    ),
)
UserNotificationService = UserNotificationsEmail()
