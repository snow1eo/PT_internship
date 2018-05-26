import importlib
from shlex import quote

from modules.functions import get_compliance_env
from modules.statuses import Status
from modules.transports import get_transport, close_all_connections

test = importlib.import_module('.000_test_file_exist', package='scripts')


def test_compliant(run_docker):
    env = get_compliance_env('000')
    env['filename'] = quote(env['filename'])
    ssh = get_transport('SSH')
    ssh.execute('touch "{filename}"'.format(**env))
    assert test.main()[0] == Status.COMPLIANT


def test_not_compliant(run_docker):
    env = get_compliance_env('000')
    env['filename'] = quote(env['filename'])
    ssh = get_transport('SSH')
    try:
        ssh.execute('rm -f {filename}'.format(**env))
    except Exception:
        pass
    assert test.main()[0] == Status.NOT_COMPLIANT


def test_not_applicable(run_docker, no_ssh_connections):
    close_all_connections()
    assert test.main()[0] == Status.NOT_APPLICABLE


def test_error(run_docker, no_transports):
    close_all_connections()
    assert test.main()[0] == Status.ERROR and test.main()[1]
