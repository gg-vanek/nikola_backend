from rest_framework import exceptions


class BaseLogicError(exceptions.APIException):
    pass


class UnexpectedCaseError(BaseLogicError):
    pass
