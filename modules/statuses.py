from enum import IntEnum


class Statuses(IntEnum):
    COMPLIANT = 1 # совместимо
    NOT_COMPLIANT = 2 # несовместимо
    NOT_APPLICABLE = 3 # неприменимо (отствует транспорт)
    ERROR = 4 # ошибка обработаная скриптом
    EXCEPTION = 5 # ошибка скрипта обработаная модулем main

