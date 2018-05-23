from modules.errors import TransportConnectionError
from modules.functions import get_processes, get_compliance_env
from modules.statuses import Status
from modules.transports import get_transport


def main():
    try:
        env = get_compliance_env('005')
        ssh = get_transport('SSH')
        procs = get_processes(ssh)
        for proc in procs:
            if proc[2] == env['command']:
                if proc[1] == env['euser']:
                    return Status.COMPLIANT, None
                else:
                    return Status.NOT_COMPLIANT, 'Mysql running as {}'.format(proc[1])
        return Status.NOT_APPLICABLE, 'Mysql is not running'
    except TransportConnectionError:
        return Status.NOT_APPLICABLE, 'No SSH connection'
    except Exception as e_info:
        return Status.ERROR, str(e_info)
