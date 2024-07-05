from notifications.manager.telegram import ManagerNotificationsTelegram
from notifications.user.email import UserNotificationsEmail

ManagerNotificationsService = ManagerNotificationsTelegram("not key yet")
UserNotificationService = UserNotificationsEmail()
