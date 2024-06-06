from django.db import transaction

from house_reservations.models import HouseReservation
from house_reservations_billing.models.bill import HouseReservationBill


def calculate_reservation(data) -> HouseReservation:
    promo_code = data.pop("promo_code")
    reservation = HouseReservation(**data)
    bill = HouseReservationBill(reservation=reservation, promo_code=promo_code)
    # there is an explicit call to .recalculate() in .save() method, which is not called here
    bill.recalculate()

    return reservation


def create_reservation(data):
    promo_code = data.pop("promo_code")
    reservation = HouseReservation(**data)
    # there is an explicit call to .recalculate() in .save() method
    bill = HouseReservationBill(reservation=reservation, promo_code=promo_code)

    with transaction.atomic():
        reservation.save()
        reservation.bill.save()

    return reservation
