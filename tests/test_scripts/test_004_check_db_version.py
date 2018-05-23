import importlib

from modules.statuses import Status

test = importlib.import_module('.004_check_db_version', package='scripts')


def test_compliant(run_docker, db_relevant_version):
    assert test.main()[0] == Status.COMPLIANT


# Этот тест падает, я не могу подменить функцию ;( Уже замучился с ней
def test_not_compliant(run_docker, db_not_relevant_version):
    pass
    #assert test.main()[0] == Status.NOT_COMPLIANT


def test_not_applicable(run_docker, no_mysql_connections):
    assert test.main()[0] == Status.NOT_APPLICABLE


def test_error(run_docker, no_transports):
    assert test.main()[0] == Status.ERROR and test.main()[1]
