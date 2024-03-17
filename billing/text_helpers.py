from datetime import date as Date, time as Time

NIGHT_POSITION = 'night'
EARLY_CHECK_IN_POSITION = 'early_check_in'
LATE_CHECK_OUT_POSITION = 'late_check_out'
PROMO_CODE_POSITION = 'promo_code'
EXTRA_PERSONS_POSITION = 'promo_code'

NIGHT_POSITION_DESCRIPTION_TEMPLATE = "Ночь с {start} на {end}"
EARLY_CHECK_IN_POSITION_DESCRIPTION_TEMPLATE = "Ранний въезд {date} в {time}"
LATE_CHECK_OUT_POSITION_DESCRIPTION_TEMPLATE = "Поздний выезд {date} в {time}"


def night_description(start: Date, end: Date):
    return NIGHT_POSITION_DESCRIPTION_TEMPLATE.format(start=start.strftime("%d-%m"), end=end.strftime("%d-%m"))


def early_check_in_description(date: Date, time: Time):
    return EARLY_CHECK_IN_POSITION_DESCRIPTION_TEMPLATE.format(date=date.strftime("%d-%m"),
                                                                   time=time.strftime("%H:%M"))


def late_check_out_description(date: Date, time: Time):
    return LATE_CHECK_OUT_POSITION_DESCRIPTION_TEMPLATE.format(date=date.strftime("%d-%m"),
                                                                   time=time.strftime("%H:%M"))
