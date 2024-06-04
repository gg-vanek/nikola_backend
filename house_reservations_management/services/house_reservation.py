from django.db import transaction

from house_reservations.models import HouseReservation
from house_reservations_billing.models.bill import HouseReservationBill


def calculate_reservation(data) -> HouseReservation:
    promo_code = data.pop("promo_code")
    reservation = HouseReservation(**data)
    # implicit call to bill.recalculate() in __init__ method
    bill = HouseReservationBill(reservation=reservation, promo_code=promo_code)

    return reservation


def create_reservation(data):
    reservation = calculate_reservation(data)

    with transaction.atomic():
        reservation.save()
        reservation.bill.save()

    return reservation
