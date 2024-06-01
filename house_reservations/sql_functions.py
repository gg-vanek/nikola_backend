from django.contrib.postgres.fields import DateTimeRangeField
from django.db.models import Func


class TsTzRange(Func):
    """
    Класс для создания функций TSTZRANGE в запросах к базе данных PostgreSQL.
    Используется для работы с диапазонами дат и времени в базе данных.
    """
    function = "TSTZRANGE"
    output_field = DateTimeRangeField()
