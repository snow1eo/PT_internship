from enum import IntEnum


class Status(IntEnum):
    COMPLIANT = 1
    NOT_COMPLIANT = 2
    NOT_APPLICABLE = 3
    ERROR = 4
    EXCEPTION = 5
