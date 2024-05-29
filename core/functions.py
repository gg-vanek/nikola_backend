import calendar
from datetime import date as Date


def is_holiday(day: Date) -> bool:
    KNOWN_HOLIDAYS = [  # HARDCODE
        *[(i, 1) for i in range(1, 9)],
        (23, 2),
        (8, 3),
        (29, 4),
        (30, 4),
        (1, 5),
        (9, 5), (10, 5),
        (12, 6),
        (4, 11), (30, 12), (31, 12),
    ]

    return day.weekday() in [calendar.SATURDAY, calendar.SUNDAY] or ((day.day, day.month) in KNOWN_HOLIDAYS)
