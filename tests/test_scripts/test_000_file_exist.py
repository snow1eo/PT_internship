from shlex import quote
import importlib

from modules.database import get_controls
from modules.statuses import Status
from modules.transports import get_transport, close_all_connections

test = importlib.import_module('.000_test_file_exist', package='scripts')


def test_000_file_exist_1(run_docker):
    env = get_controls()['000']['env']
    env['filename'] = quote(env['filename'])
    ssh = get_transport('SSH')
    ssh.execute('touch "{filename}"'.format(**env))
    assert test.main()[0] == Status.COMPLIANT


def test_000_file_exist_2(run_docker):
    env = get_controls()['000']['env']
    env['filename'] = quote(env['filename'])
    ssh = get_transport('SSH')
    try:
        ssh.execute('rm -f {filename}'.format(**env))
    except Exception:
        pass
    assert test.main()[0] == Status.NOT_COMPLIANT


def test_000_file_exist_3(run_docker, no_ssh_connections):
    close_all_connections()
    assert test.main()[0] == Status.NOT_APPLICABLE


def test_000_file_exist_4(run_docker, no_transports):
    close_all_connections()
    assert test.main()[0] == Status.ERROR and test.main()[1]
