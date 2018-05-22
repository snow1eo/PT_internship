import importlib

from modules.statuses import Status

test = importlib.import_module('.005_check_euser_mysqld', package='scripts')


def test_compliant(run_docker):
    # TODO
    pass


def test_not_compliant(run_docker):
    # TODO
    pass

def test_not_applicable(no_ssh_connections):
    assert test.main()[0] == Status.NOT_APPLICABLE


def test_error(no_transports):
    assert test.main()[0] == Status.ERROR and test.main()[1]
