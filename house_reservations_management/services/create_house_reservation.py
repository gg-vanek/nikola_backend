from django.db import transaction

from house_reservations.models import HouseReservation
from house_reservations_billing.models import HouseReservationBill
from house_reservations_billing.services.bill import initialize_bill


def calculate_reservation(data) -> HouseReservation:
    promo_code = data.pop("promo_code")
    reservation = HouseReservation(**data)
    bill = HouseReservationBill(reservation=reservation, promo_code=promo_code)
    initialize_bill(bill)

    return reservation


def create_reservation(data):
    reservation, bill = calculate_reservation(data)

    with transaction.atomic():
        reservation.save()
        reservation.bill.save()

    return reservation
