from celery import shared_task

from house_reservations.models import HouseReservation
from notifications import UserNotificationService, ManagerNotificationsService


@shared_task
def new_reservation_created_manager_notification(reservation_id: int):
    reservation = HouseReservation.objects.get(id=reservation_id)
    return ManagerNotificationsService.new_reservation_created(reservation)


@shared_task
def new_reservation_created_user_notification(reservation_id: int):
    reservation = HouseReservation.objects.get(id=reservation_id)
    return UserNotificationService.new_reservation_created(reservation)


@shared_task
def remind_manager_about_unapproved_reservations():
    reservations = HouseReservation.objects.filter(id=1)  # TODO
    ManagerNotificationsService.there_are_some_unapproved_reservations(reservations)


@shared_task
def archive_outdated_reservations():
    reservations = HouseReservation.objects.filter(id=1)  # TODO
    ManagerNotificationsService.there_are_some_unapproved_reservations(reservations)
