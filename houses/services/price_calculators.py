from dataclasses import dataclass, field
from datetime import date as Date, datetime as Datetime, time as Time, timedelta

import logging

from core.errors import LogicError, IncorrectPeopleAmountInReservationException, \
    IncorrectDatetimesException, IncorrectTimeException
from core.models import Pricing
from events.models import Event
from houses.models import House
logger = logging.getLogger(__name__)


@dataclass()
class ReceiptPosition:
    price: int
    date: Date
    time: Time | None = None
    type: str = "night"
    name: str = field(init=False)

    def __post_init__(self):
        try:
            self.price = int(round(self.price, -2))
            if self.type == "night":
                assert self.time is None
                self.name = f"Ночь {(self.date - timedelta(days=1)).strftime('%d.%m')}-{self.date.strftime('%d.%m')}"
            elif self.type == "early_check_in":
                assert isinstance(self.time, Time)
                self.name = f"Ранний въезд {self.date.strftime('%d.%m')} в {self.time.strftime('%H:%M')}"
            elif self.type == "late_check_out":
                assert isinstance(self.time, Time)
                self.name = f"Поздний выезд {self.date.strftime('%d.%m')} в {self.time.strftime('%H:%M')}"
            else:
                assert False, f"unexpected self.type = {self.type}"
        except AssertionError as e:
            raise LogicError(str(e)) from e


@dataclass
class Receipt:
    nights: list[ReceiptPosition] = field(default_factory=list)
    extra_services: list[ReceiptPosition] = field(default_factory=list)
    total: int = 0
    nights_total: int = 0
    extra_services_total: int = 0

    def __post_init__(self):
        for night in self.nights:
            assert night.type == "night"
            self.total += night.price
            self.nights_total += night.price
        for extra_service in self.extra_services:
            assert extra_service.type != "night"
            self.total += extra_service.price
            self.extra_services_total += extra_service.price

    def add_position(self, position: ReceiptPosition):
        if position.price != 0:
            if position.type == "night":
                self.nights.append(position)
                self.nights_total += position.price
            else:
                self.extra_services.append(position)
                self.extra_services_total += position.price
            self.total += position.price


def calculate_reservation_receipt(house: House | int,
                                  check_in_datetime: Datetime, check_out_datetime: Datetime,
                                  extra_persons_amount: int) -> Receipt:
    if isinstance(house, int):
        try:
            house = House.objects.get(pk=house)
        except House.DoesNotExist as e:
            raise LogicError(f"Некорректный id домика = {house}") from e

    if extra_persons_amount < 0:
        raise IncorrectPeopleAmountInReservationException(f"Отрицательное количество людей в заявке: {extra_persons_amount}")
    if extra_persons_amount + house.base_persons_amount > house.max_persons_amount:
        raise IncorrectPeopleAmountInReservationException(f"Слишком много дополнительных людей в заявке: {extra_persons_amount} + {house.base_persons_amount} > {house.max_persons_amount}")
    if check_in_datetime >= check_out_datetime:
        raise IncorrectDatetimesException(f"Некорректные дата и время въезда и выезда (въезд позже выезда): {check_in_datetime.strftime('%d-%m-%Y %H:%M')} >= {check_out_datetime.strftime('%d-%m-%Y')}")
    if check_in_datetime.time() not in Pricing.ALLOWED_CHECK_IN_TIMES:
        raise IncorrectTimeException(f"Некорректное время въезда: {check_in_datetime.time().strftime('%H:%M')}")
    if check_out_datetime.time() not in Pricing.ALLOWED_CHECK_OUT_TIMES:
        raise IncorrectTimeException(f"Некорректное время выезда: {check_in_datetime.time().strftime('%H:%M')}")

    check_in_date = check_in_datetime.date()
    check_in_time = check_in_datetime.time()

    check_out_date = check_out_datetime.date()
    check_out_time = check_out_datetime.time()

    receipt = Receipt()

    # увеличение стоимости за ранний въезд
    early_check_in = ReceiptPosition(
        type="early_check_in",
        time=check_in_time,
        date=check_in_date,
        price=Pricing.ALLOWED_CHECK_IN_TIMES.get(check_in_time, 0) *
              calculate_house_price_by_day(house, check_in_date)
    )
    receipt.add_position(position=early_check_in)

    late_check_out = ReceiptPosition(
        type="late_check_out",
        time=check_out_time,
        date=check_out_date,
        price=Pricing.ALLOWED_CHECK_OUT_TIMES.get(check_out_time, 0) *
              calculate_house_price_by_day(house, check_out_date)
    )
    receipt.add_position(position=late_check_out)

    # мы с мамой договорились, что "ночь идет перед днем"
    # иными словами множитель выходного дня применяется к ночам пт-сб и сб-вс, но не к вс-пн
    date = check_in_date + timedelta(days=1)
    while date <= check_out_date:
        receipt.add_position(position=ReceiptPosition(
            type="night", date=date,
            price=calculate_house_price_by_day(house, date) +
                  extra_persons_amount * house.price_per_extra_person))
        date = date + timedelta(days=1)

    return receipt


def calculate_house_price_by_day(house: House, day: Date) -> int:
    # TODO в этой функции нужно принимать не house, а house_id, base_price, holidays_multiplier

    price = house.base_price
    # TODO events нужно доставать из кэша, потому что их мало
    events = Event.objects.filter(start_date__lte=day, end_date__gte=day)

    if is_holiday(day):
        price *= house.holidays_multiplier

    for event in events:
        price *= event.multiplier

    price = int(round(price, -2))

    return price


def is_holiday(day: Date) -> bool:
    # код ниже очень долго работает. Никто не будет 15 секунд ждать календарь

    # cached_day = cache.get(day)
    # if cached_day:
    #     return cached_day
    #
    # # logger.error(requests.get("https://isdayoff.ru/"+day.strftime("%Y-%m-%d")).text)
    # is_holiday_flag = bool(int(requests.get("https://isdayoff.ru/"+day.strftime("%Y-%m-%d")).text))
    #
    # cache.set(day, is_holiday_flag, timeout=60*60*12)  # раз в 12 часов будет эта инфа обновляться
    #
    # return is_holiday_flag
    return day.weekday() in [5, 6]
