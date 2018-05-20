import importlib

from modules.statuses import Status

test = importlib.import_module('.003_check_dump_for_pass', package='scripts')


def test_003_mem_dump_1(run_docker, no_ssh_execute):
    assert test.main()[0] == Status.COMPLIANT


def test_003_mem_dump_2(run_docker):
    assert test.main()[0] == Status.NOT_COMPLIANT


def test_003_mem_dump_3(run_docker, no_ssh_connections):
    assert test.main()[0] == Status.NOT_APPLICABLE


def test_003_mem_dump_4(run_docker, no_transports):
    assert test.main()[0] == Status.ERROR and test.main()[1]
