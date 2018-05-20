import importlib

from modules.database import get_controls
from modules.statuses import Status
from modules.transports import get_transport, close_all_connections

test = importlib.import_module('.002_file_permissions', package='scripts')


def test_002_permissions_1(run_docker):
    env = get_controls()['002']['env']
    ssh = get_transport('SSH')
    ssh.execute('chmod {permissions} "{filename}"'.format(**env))
    ssh.execute('chown {owner}:{group} "{filename}"'.format(**env))
    assert test.main()[0] == Status.COMPLIANT


def test_002_permissions_2(run_docker):
    env = get_controls()['002']['env']
    ssh = get_transport('SSH')
    ssh.execute('chmod {permissions} "{filename}"'.format(
        permissions=int(env['permissions']) ^ 1,
        filename=env['filename']))
    assert test.main()[0] == Status.NOT_COMPLIANT


def test_002_permissions_3(run_docker, no_ssh_connections):
    close_all_connections()
    assert test.main()[0] == Status.NOT_APPLICABLE


def test_002_permissions_4(run_docker, no_transports):
    close_all_connections()
    assert test.main()[0] == Status.ERROR and test.main()[1]
