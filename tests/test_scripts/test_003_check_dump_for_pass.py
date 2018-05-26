import importlib

from modules.statuses import Status

test = importlib.import_module('.003_check_dump_for_pass', package='scripts')


def test_compliant(run_docker, no_ssh_execute):
    assert test.main()[0] == Status.COMPLIANT


def test_not_compliant(run_docker):
    assert test.main()[0] == Status.NOT_COMPLIANT


def test_not_applicable(run_docker, no_ssh_connections):
    assert test.main()[0] == Status.NOT_APPLICABLE


def test_error(run_docker, no_transports):
    assert test.main()[0] == Status.ERROR and test.main()[1]
