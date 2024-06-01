from django.core.exceptions import ValidationError
from django.utils.timezone import now

from core.errors import LogicError
from clients.models import Client
from house_reservations_billing.models import (
    HouseReservationPromoCode,
    FIXED_VALUE_DISCOUNT,
    PERCENTAGE_DISCOUNT, HouseReservationBill,
)


def apply(promo_code: HouseReservationPromoCode, value: int) -> int:
    if promo_code.discount_type == FIXED_VALUE_DISCOUNT:
        return max(
            100,
            value - promo_code.discount_value,
        )
    elif promo_code.discount_type == PERCENTAGE_DISCOUNT:
        return max(
            100,
            round(value * (100 - promo_code.discount_value) // 100, -2),
        )
    else:
        raise LogicError(f"Unexpected promo_code type: '{promo_code.discount_type}'")


def check_availability(
        promo_code: HouseReservationPromoCode,
        bill: HouseReservationBill,
        client: Client,
        value: int,
):
    # Check dates
    if promo_code.issuance_datetime and now() < promo_code.issuance_datetime:
        raise ValidationError(
            f"Промокод можно будет активировать с {promo_code.issuance_datetime.strftime('%d-%m-%Y %H:%M')}",
        )
    if promo_code.expiration_datetime and now() > promo_code.expiration_datetime:
        raise ValidationError(f"Промокод истек {promo_code.expiration_datetime.strftime('%d-%m-%Y %H:%M')}")

    # Check client
    if promo_code.client and client:  # когда происходит запрос цены бронирования информация приходит без клиента
        if promo_code.client != client:
            raise ValidationError(f"Промокод принадлежит другому пользователю (идентификация по email)")

    # Check usages count
    if bill.id and promo_code.bills.filter(id=bill.id):  # если чек уже сохранен в бд с этим промокодом
        pass
    elif promo_code.bills.count() >= promo_code.max_use_times:
        raise ValidationError('Промокод уже был использован максимальное количество раз')

    # Check bill value
    if value < promo_code.minimal_bill_value:
        raise ValidationError(f'Промокод доступен при сумме в чеке от {promo_code.minimal_bill_value}')
