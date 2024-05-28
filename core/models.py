from datetime import time as Time


class Pricing:
    MIN_HOUSE_BASE_PRICE = 5000
    # "Минимальная базовая цена домика",
    # "Ты точно хочешь разрешить стравить цену меньше 5000?"

    MIN_HOUSE_HOLIDAYS_MULTIPLIER = 1
    # "Минимальный множитель цены домика в выходные и праздничные дни", \
    # f"Ты точно хочешь разрешить стравить множитель в выходные и праздничные дни меньше 1?"

    ALLOWED_CHECK_OUT_TIMES = {
        'default': Time(hour=12),
        'earliest': Time(hour=12),
        'latest': Time(hour=15),
        Time(hour=12): 0,
        Time(hour=15): 0.3,  # поздний выезд - доплата 30% от стоимости дневного проживания в день выезда
    }

    ALLOWED_CHECK_IN_TIMES = {
        'default': Time(hour=16),
        'earliest': Time(hour=13),
        'latest': Time(hour=16),
        Time(hour=16): 0,
        Time(hour=13): 0.3,  # ранний въезд - доплата 30% от стоимости дневного проживания в день въезда
    }

    @staticmethod
    def serializable_times_dict(d: dict):
        times = []

        for k, v in d.items():
            if isinstance(k, Time):
                times.append(k)

        times.sort()
        times = [t.strftime("%H:%M") for t in times]

        return {"default": d["default"].strftime("%H:%M"), "times": times}

    def __str__(self):
        return "Configuration"
