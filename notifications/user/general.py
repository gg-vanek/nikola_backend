from abc import ABC, abstractmethod

from house_reservations.models import HouseReservation


class UserNotificationsBaseClass(ABC):
    @abstractmethod
    def new_reservation_created(self, reservation: HouseReservation):
        pass
