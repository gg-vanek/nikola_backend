from abc import ABC, abstractmethod

from house_reservations.models import HouseReservation


class ManagerNotificationsBaseClass(ABC):
    @abstractmethod
    def new_reservation_created(self, reservation: HouseReservation):
        pass

    @abstractmethod
    def there_are_some_unapproved_reservations(self, reservations: list[HouseReservation]):
        pass
