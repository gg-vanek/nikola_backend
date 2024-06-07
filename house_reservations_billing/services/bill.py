from datetime import timedelta

from core.models import Pricing
from house_reservations_billing.services.price_calculators import calculate_house_price_by_day, \
    calculate_extra_persons_price
from house_reservations_billing.services.promocode import apply, check_availability
from house_reservations_billing.services.text_helpers import (
    EARLY_CHECK_IN_POSITION,
    early_check_in_description,
    NIGHT_POSITION,
    night_description,
    LATE_CHECK_OUT_POSITION,
    late_check_out_description,
    EXTRA_PERSONS_POSITION,
    PROMO_CODE_POSITION,
)


def initialize_bill(bill):
    house = bill.reservation.house

    check_in_date = bill.reservation.local_check_in_datetime.date()
    check_in_time = bill.reservation.local_check_in_datetime.time()

    check_out_date = bill.reservation.local_check_out_datetime.date()
    check_out_time = bill.reservation.local_check_out_datetime.time()

    non_chronological_positions = []
    chronological_positions = []

    # NOTE: ночь идет перед днем
    # иными словами множитель выходного дня применяется к ночам пт-сб и сб-вс, но не к вс-пн
    date = check_in_date + timedelta(days=1)
    while date <= check_out_date:
        chronological_positions.append({
            "type": NIGHT_POSITION,
            "start_date": date - timedelta(days=1),
            "end_date": date,
            "price": calculate_house_price_by_day(house, date),
            "description": night_description(date - timedelta(days=1), date)
        })
        date = date + timedelta(days=1)

    # увеличение стоимости за ранний въезд и поздний выезд
    early_check_in = {
        "type": EARLY_CHECK_IN_POSITION,
        "time": check_in_time,
        "date": check_in_date,
        "price": Pricing.ALLOWED_CHECK_IN_TIMES.get(check_in_time, 0) *
                 calculate_house_price_by_day(house, check_in_date),
        "description": early_check_in_description(check_in_date, check_in_time)
    }
    if early_check_in["price"] != 0:
        chronological_positions.insert(0, early_check_in)

    late_check_out = {
        'type': LATE_CHECK_OUT_POSITION,
        "time": check_out_time,
        "date": check_out_date,
        "price": Pricing.ALLOWED_CHECK_OUT_TIMES.get(check_out_time, 0) *
                 calculate_house_price_by_day(house, check_out_date),
        "description": late_check_out_description(check_out_date, check_out_time)
    }
    if late_check_out["price"] != 0:
        chronological_positions.append(late_check_out)

    # увеличение стоимости за дополнительных людей
    extra_persons_amount = max(0, bill.reservation.total_persons_amount - house.base_persons_amount)
    price_per_extra_person = house.price_per_extra_person
    nights_amount = (check_out_date - check_in_date).days

    if extra_persons_amount > 0:
        non_chronological_positions.append(
            {
                "type": EXTRA_PERSONS_POSITION,
                "extra_persons_amount": extra_persons_amount,
                "price_per_extra_person": price_per_extra_person,
                "nights_amount": nights_amount,
                "price": calculate_extra_persons_price(house, bill.reservation.total_persons_amount) * nights_amount,
                "description": f"{extra_persons_amount} доп. гостей х {nights_amount} ночей",
            }
        )

    if bill.promo_code:
        price_without_discount = sum(
            [ch_p["price"] for ch_p in chronological_positions] +
            [g_p["price"] for g_p in non_chronological_positions]
        )

        check_availability(bill.promo_code, bill, bill.reservation.client, price_without_discount)
        price_with_discount = apply(bill.promo_code, price_without_discount)
        discount = price_with_discount - price_without_discount

        non_chronological_positions.append(
            {
                "type": PROMO_CODE_POSITION,
                "promo_code": bill.promo_code.code,
                "price": discount,
                "description": str(bill.promo_code),
            }
        )

    bill.chronological_positions = chronological_positions
    bill.non_chronological_positions = non_chronological_positions

    bill.total = sum(
        [ch_p["price"] for ch_p in chronological_positions] + [g_p["price"] for g_p in non_chronological_positions])
