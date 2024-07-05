import logging

from house_reservations.models import HouseReservation
from notifications.user.general import UserNotificationsBaseClass

from django.conf import settings

from notifications.user.templates import NEW_RESERVATION_CREATED

logger = logging.getLogger(__name__)


class UserNotificationsEmail(UserNotificationsBaseClass):

    def new_reservation_created(self, reservation: HouseReservation):
        return NEW_RESERVATION_CREATED.format(
            reservation_house_name=reservation.house.name,
            reservation_check_in_datetime=reservation.check_in_datetime.strftime("%d-%m %H:%M"),
            reservation_check_out_datetime=reservation.check_out_datetime.strftime("%d-%m %H:%M"),
            reservation_slug=reservation.slug,
            host=settings.ALLOWED_HOSTS[0],
        )
