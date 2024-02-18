class LogicError(Exception):
    pass


class IncorrectDatesException(LogicError):
    pass


class IncorrectDatetimesException(LogicError):
    pass


class IncorrectTimeException(LogicError):
    pass


class IncorrectPeopleAmountInReservationException(LogicError):
    pass

