from rest_framework import exceptions
from rest_framework.exceptions import ValidationError


class BaseLogicError(exceptions.APIException):
    pass


class UnexpectedCaseError(BaseLogicError):
    def __init__(self, detail: str):
        super().__init__(detail={"logic": detail})


class PromoCodeValidationError(BaseLogicError, ValidationError):
    def __init__(self, detail: str):
        super(ValidationError, self).__init__(detail={"promocode": detail})
