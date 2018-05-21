import importlib

from modules.database import get_controls
from modules.statuses import Status
from modules.transports import get_transport

test = importlib.import_module('.004_check_db_version', package='scripts')


def test_004_check_db_version_1(run_docker, db_relevant_version):
    assert test.main()[0] == Status.COMPLIANT


def test_004_check_db_version_2(run_docker, db_not_relevant_version):
    assert test.main()[0] == Status.NOT_COMPLIANT


def test_004_check_db_version_3(run_docker, no_mysql_connections):
    assert test.main()[0] == Status.NOT_APPLICABLE


def test_004_check_db_version_4(run_docker, no_transports):
    assert test.main()[0] == Status.ERROR and test.main()[1]
