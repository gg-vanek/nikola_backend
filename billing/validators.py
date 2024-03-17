"""Выяснилось что этот валидатор не нужен, потому что при сохранении объекта в бд
автоматически происходит изменение поля и оно не может быть некорректным

Но валидатор написан хорошо и я не буду его удалять"""

from django.core.exceptions import ModelValidationError

from billing.json_mappers import DATE_FORMAT, TIME_FORMAT
from billing.text_helpers import *


class ChronologicalPositionsValidator:
    def __call__(self, chronological_positions):
        errors = []
        for i in range(len(chronological_positions)):
            position = chronological_positions[i]
            prefix = f"Incorrect position at index {i}: "

            if position.get("type") == NIGHT_POSITION:
                price_error = self.validate_price(position, prefix)
                start_date_error = self.validate_date(position, prefix, "start_date")
                end_date_error = self.validate_date(position, prefix, "end_date")
                description_error = self.validate_description(
                    position=position, prefix=prefix,
                    dependencies=not start_date_error and not end_date_error,
                    func=night_description,
                    func_kwargs={"start": position.get("start_date"), "end": position.get("end_date")},
                )
                errors.extend([err for err in [price_error, start_date_error, end_date_error, description_error] if err])

            elif position.get("type") == EARLY_CHECK_IN_POSITION:
                price_error = self.validate_price(position, prefix)
                time_error = self.validate_time(position, prefix, "time")
                date_error = self.validate_date(position, prefix, "date")
                description_error = self.validate_description(
                    position=position, prefix=prefix,
                    dependencies=not time_error and not date_error,
                    func=early_check_in_description,
                    func_kwargs={"time": position.get("time"), "date": position.get("date")},
                )
                errors.extend([err for err in [price_error, time_error, date_error, description_error] if err])

            elif position.get("type") == LATE_CHECK_OUT_POSITION:
                price_error = self.validate_price(position, prefix)
                time_error = self.validate_time(position, prefix, "time")
                date_error = self.validate_date(position, prefix, "date")
                description_error = self.validate_description(
                    position=position, prefix=prefix,
                    dependencies=not time_error and not date_error,
                    func=late_check_out_description,
                    func_kwargs={"time": position.get("time"), "date": position.get("date")},
                )
                errors.extend([err for err in [price_error, time_error, date_error, description_error] if err])

            else:
                raise ModelValidationError(f"Unexpected position type {position.get('type')}")

    def validate_date(self, position, prefix, key):
        if key not in position:
            return ModelValidationError(prefix + f"'{key}' key not found")
        elif not isinstance(position[key], Date):
            return ModelValidationError(
                prefix + f"value at '{key}' key can not be parsed as Date. Expected format `{DATE_FORMAT}`")

    def validate_time(self, position, prefix, key):
        if key not in position:
            return ModelValidationError(prefix + f"'{key}' key not found")
        elif not isinstance(position[key], Date):
            return ModelValidationError(
                prefix + f"value at '{key}' key can not be parsed as Time. Expected format `{TIME_FORMAT}`")

    def validate_price(self, position, prefix):
        if "price" not in position:
            return ModelValidationError(prefix + "'price' key not found")
        elif not isinstance(position["price"], int):
            return ModelValidationError(prefix + f"value at 'price' key can not be interpreted as int")
        elif not position["price"] % 100 == 0:
            return ModelValidationError(prefix + f"value at 'price' has to be integer rounded to hundreds")

    def validate_description(self, position, prefix, dependencies, func, func_kwargs):
        if "description" not in position:
            return ModelValidationError(prefix + "'description' key not found")
        elif dependencies and func(**func_kwargs) != position["description"]:
            ModelValidationError(prefix + f"'description' value is incorrect: expected `{func(**func_kwargs)}`")
