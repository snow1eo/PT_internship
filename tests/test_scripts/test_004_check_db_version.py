import importlib

from modules.functions import get_compliance_env
from modules.statuses import Status

test = importlib.import_module('.004_check_db_version', package='scripts')


def test_compliant(run_docker, monkeypatch):
    ver = get_compliance_env('004')['relevant_version']
    monkeypatch.setattr(test, 'get_sql_version',
                        lambda x: ver)
    assert test.main()[0] == Status.COMPLIANT


def test_not_compliant(run_docker, monkeypatch):
    ver = get_compliance_env('004')['relevant_version']
    monkeypatch.setattr(test, 'get_sql_version',
                        lambda x: ver + 'wrong')
    assert test.main()[0] == Status.NOT_COMPLIANT


def test_not_applicable(run_docker, no_mysql_connections):
    assert test.main()[0] == Status.NOT_APPLICABLE


def test_error(run_docker, no_transports):
    assert test.main()[0] == Status.ERROR and test.main()[1]
