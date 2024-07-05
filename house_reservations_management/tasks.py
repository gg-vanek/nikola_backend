from celery import shared_task
from house_reservations.models import HouseReservation

from notifications import UserNotificationService, ManagerNotificationsService


@shared_task
def send_telegram_notification(reservation_id: int):
    reservation = HouseReservation.objects.get(id=reservation_id)
    ManagerNotificationsService.new_reservation_created(reservation)


@shared_task
def send_email_to_user(reservation_id: int):
    reservation = HouseReservation.objects.get(id=reservation_id)
    UserNotificationService.new_reservation_created(reservation)


@shared_task
def remind_about_unapproved_reservations():
    reservations = HouseReservation.objects.filter(id=1)  # TODO
    ManagerNotificationsService.there_are_some_unapproved_reservations(reservations)
