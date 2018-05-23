import re

from modules.errors import TransportConnectionError
from modules.functions import get_compliance_env, get_config
from modules.statuses import Status
from modules.transports import get_transport


def main():
    try:
        conf_name = get_compliance_env('006')['conf_name']
        ssh = get_transport('SSH')
        conf = get_config(ssh, conf_name)
        valuated_options = get_valuated_options(conf)
        if 'password' not in valuated_options:
            return Status.COMPLIANT, None
        else:
            return Status.NOT_COMPLIANT, \
                "Password using: {password}".format(**valuated_options)
    except TransportConnectionError:
        return Status.NOT_APPLICABLE, 'No SSH connection'
    except Exception as e_info:
        return Status.ERROR, str(e_info)


def get_valuated_options(conf):
    pattern = re.compile(r'(\w+)\s*=\s*(\w+)\n')
    return {key: value for key, value in re.findall(pattern, conf)}
