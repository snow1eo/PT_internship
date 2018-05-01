from enum import IntEnum


class Statuses(IntEnum):
    COMPLIANT = 1
    NOT_COMPLIANT = 2
    NOT_APPLICABLE = 3
    ERROR = 4
    EXCEPTION = 5


def get_status_name(code):
    for status in Statuses:
        if status.value == code:
            return status.name
