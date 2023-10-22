import logging
from datetime import date as Date, datetime as Datetime, timedelta

from core.models import Pricing
from events.models import Event
from houses.models import House

logger = logging.getLogger(__name__)


class ReceiptPosition:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def __str__(self):
        return f"{self.name} - {self.price}"


class Receipt:
    def __init__(self):
        self.positions = []
        self.total = 0

    def add_position(self, position: ReceiptPosition):
        if position.price != 0:
            self.positions.append(position)
            self.total += position.price

    def full_receipt_str(self):
        return '\n'.join([str(position) for position in self.positions] + [str(self)])

    def __str__(self):
        return f'---{self.total}---'


def calculate_reservation_price(house: House | int,
                                check_in_datetime: Datetime, check_out_datetime: Datetime,
                                extra_persons_amount: int,
                                ) -> int:
    receipt = calculate_reservation_price_receipt(house,
                                                  check_in_datetime, check_out_datetime,
                                                  extra_persons_amount, )
    logger.debug('\n------------------------------------------\n' +
                 receipt.full_receipt_str() +
                 '\n------------------------------------------\n')
    return receipt.total


def calculate_reservation_price_receipt(house: House | int,
                                        check_in_datetime: Datetime, check_out_datetime: Datetime,
                                        extra_persons_amount: int,
                                        ) -> Receipt:
    if type(house) == int:
        house = House.objects.get(pk=house)

    # TODO защита от
    #  1) отрицательного количество extra_persons_amount
    #  2) дата выезда меньше даты въезда
    #  3) некорректное время въезда или выезда
    if extra_persons_amount < 0:
        extra_persons_amount = 0

    check_in_date = check_in_datetime.date()
    check_in_time = check_in_datetime.time()

    check_out_date = check_out_datetime.date()
    check_out_time = check_out_datetime.time()

    receipt = Receipt()

    # увеличение стоимости за ранний въезд
    early_check_in = ReceiptPosition(
        name=f"Ранний въезд {check_in_date.strftime('%d.%m')} ({check_in_time.strftime('%H:%M')})",
        price=round(Pricing.ALLOWED_CHECK_IN_TIMES.get(check_in_time, 0) *
                    calculate_house_price_by_day(house, check_in_date), -2)
    )
    receipt.add_position(position=early_check_in)

    # увеличение стоимости за поздний выезд (добавляется в чек в конце функции)
    late_check_out = ReceiptPosition(
        name=f"Ранний выезд {check_out_date.strftime('%d.%m')} ({check_out_time.strftime('%H:%M')})",
        price=round(Pricing.ALLOWED_CHECK_OUT_TIMES.get(check_out_time, 0) *
                    calculate_house_price_by_day(house, check_out_date), -2)
    )

    # мы с мамой договорились, что "ночь идет перед днем"
    # иными словами множитель выходного дня применяется к ночам пт-сб и сб-вс, но не к вс-пн
    date = check_in_date + timedelta(days=1)
    while date <= check_out_date:
        receipt.add_position(position=ReceiptPosition(
            name=f"Ночь {(date - timedelta(days=1)).strftime('%d.%m')}-{date.strftime('%d.%m')}",
            price=calculate_house_price_by_day(house, date) +
                  round(extra_persons_amount * house.price_per_extra_person, -2)))
        date = date + timedelta(days=1)

    receipt.add_position(position=late_check_out)

    return receipt


def calculate_house_price_by_day(house, day: Date) -> int:
    price = house.base_price
    events = Event.objects.filter(start_date__lte=day, end_date__gte=day)

    if is_holiday(day):
        price *= house.holidays_multiplier

    for event in events:
        price *= event.multiplier

    return round(price, -2)


def is_holiday(day: Date):
    return day.weekday() in [5, 6]
