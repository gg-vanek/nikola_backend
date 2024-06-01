from datetime import datetime as Datetime

from django.core.exceptions import ValidationError
from django.utils.timezone import now

from core.models import Pricing
from houses.models import House

# TODO IncorrectPeopleAmountInReservationException
# TODO IncorrectDatetimesException

def clean_total_persons_amount(total_persons_amount: int, house: House):
    if total_persons_amount < 0:
        raise ValidationError("Невозможно заселить отрицательное количество человек в домик")
    if not (1 <= total_persons_amount <= house.max_persons_amount):
        raise ValidationError(f"Невозможно заселить столько человек в домик: \n"
                              f"Минимальное количество человек: {house.base_persons_amount}\n"
                              f"Максимальное количество человек: {house.max_persons_amount}"
                              f"Указанное количество человек: {total_persons_amount}")


def clean_check_in_datetime(check_in_datetime: Datetime):
    if check_in_datetime.time() not in Pricing.ALLOWED_CHECK_IN_TIMES:
        raise ValidationError(f"Недопустимое время ВЪЕЗДА - {check_in_datetime}. "
                              f"Доступное время - {Pricing.ALLOWED_CHECK_IN_TIMES.keys()}")


def clean_check_out_datetime(check_out_datetime: Datetime):
    if check_out_datetime.time() not in Pricing.ALLOWED_CHECK_OUT_TIMES:
        raise ValidationError(f"Недопустимое время ВЫЕЗДА - {check_out_datetime}. "
                              f"Доступное время - {Pricing.ALLOWED_CHECK_OUT_TIMES.keys()}")


def check_datetime_fields(check_in_datetime: Datetime, check_out_datetime: Datetime):
    if check_in_datetime.date() <= now().date():
        raise ValidationError("Невозможно забронировать домик на прошедшую дату")

    if check_in_datetime >= check_out_datetime:
        raise ValidationError("Дата и время заезда должны быть строго меньше даты и времени выезда")
