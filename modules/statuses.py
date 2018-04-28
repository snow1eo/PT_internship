"""Статусы выполнения теста, записываемые в базу данных"""

STATUS_COMPLIANT      = 1 # совместимо
STATUS_NOT_COMPLIANT  = 2 # несовместимо
STATUS_NOT_APPLICABLE = 3 # неприменимо (отствует транспорт)
STATUS_ERROR          = 4 # ошибка обработаная скриптом
STATUS_EXCEPTION      = 5 # ошибка скрипта, обработаная модулем main
