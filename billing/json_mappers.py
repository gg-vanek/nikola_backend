from datetime import datetime as Datetime, date as Date, time as Time
from json import JSONEncoder, JSONDecoder
import json
import re

# DATETIME_FORMAT = "%d-%m-%Y %H:%M"
DATE_FORMAT = "%d-%m-%Y"
TIME_FORMAT = "%H:%M"


class ChronologicalPositionsEncoder(JSONEncoder):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self.ensure_ascii = False
        self.sort_keys = True
        self.indent = 2

    def default(self, o):
        if isinstance(o, Date):
            return o.strftime(DATE_FORMAT)
        elif isinstance(o, Time):
            return o.strftime(TIME_FORMAT)
        else:
            return super().default(o)


class ChronologicalPositionsDecoder(JSONDecoder):

    def decode(self, s, _w=json.decoder.WHITESPACE.match):
        result = super().decode(s, _w)  # вызовем оригинальный decode
        # Если есть поле "date", пытаемся его преобразовать

        result = self._recursive_transform(result, ".*date", lambda x: Datetime.strptime(x, DATE_FORMAT).date())
        result = self._recursive_transform(result, ".*time", lambda x: Datetime.strptime(x, TIME_FORMAT).time())

        return result

    def _recursive_transform(self, obj, transformed_key_pattern, transformation_rule):
        if isinstance(obj, dict):  # Если текущий объект - словарь
            for key, value in obj.items():
                if re.match(transformed_key_pattern, key):  # Если мы нашли ключ transformed_key
                    try:
                        # Пытаемся преобразовать значение согласно transformation_rule
                        obj[key] = transformation_rule(value)
                    except Exception as e:  # Если не получилось - продолжаем
                        pass
                else:
                    # Если текущее значение - вложенный словарь или список,
                    # обрабатываем его рекурсивно
                    obj[key] = self._recursive_transform(value, transformed_key_pattern, transformation_rule)
        elif isinstance(obj, list):  # Если текущий объект - список
            for i in range(len(obj)):
                # Обрабатываем каждый элемент рекурсивно
                obj[i] = self._recursive_transform(obj[i], transformed_key_pattern, transformation_rule)
        # Если объект не словарь и не список, оставляем его без изменений
        return obj
