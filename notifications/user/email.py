import logging
import smtplib

from house_reservations.models import HouseReservation
from notifications.user.general import UserNotificationsBaseClass

from django.conf import settings

from notifications.user.templates import NEW_RESERVATION_CREATED

logger = logging.getLogger(__name__)


class UserNotificationsEmail(UserNotificationsBaseClass):
    email_login: str
    email_password: str

    def __init__(self, email_login: str, email_password: str):
        self.email_login = email_login
        self.email_password = email_password

    def send_email(self, client_email, message):
        smtp_object = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_object.starttls()
        smtp_object.login(self.email_login, self.email_password)

        return smtp_object.sendmail(
            from_addr=self.email_login,
            to_addrs=client_email,
            msg=message.encode('utf-8'),
        )

    def new_reservation_created(self, reservation: HouseReservation):
        return self.send_email(
            reservation.client.email,
            NEW_RESERVATION_CREATED.format(
                sender_email=self.email_login,
                receiver_email=reservation.client.email,
                reservation_house_name=reservation.house.name,
                reservation_check_in_datetime=reservation.check_in_datetime.strftime("%d-%m %H:%M"),
                reservation_check_out_datetime=reservation.check_out_datetime.strftime("%d-%m %H:%M"),
                reservation_slug=reservation.slug,
                host=settings.ALLOWED_HOSTS[0],
            )
        )
