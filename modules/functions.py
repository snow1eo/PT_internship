import os
import re
from shlex import quote

from modules.database import get_controls

# General


def get_compliance_env(num):
    return get_controls()[num]['env'].copy()

# SQL


def get_global_variables(sql):
    return {
        var['VARIABLE_NAME']: var['VARIABLE_VALUE'] for var in
        sql.load_table('information_schema.global_variables')
    }


def check_vars_value(sql, var, value):
    return sql.get_global_variables()[var] == value


def get_sql_version(sql):
    pattern = re.compile(r'\d+\.\d+\.\d+')
    version = re.findall(pattern, get_global_variables(sql)['VERSION'])
    return 'unknown' if not version else version[0]

# SSH


def get_processes(ssh):
    return [x.split() for x in
            ssh.execute_show('ps -eo pid,euser,comm').splitlines()[1:-1]]


def get_config(conf_name):
    ssh = get_transport('SSH')
    conf = clear_config(ssh.get_file(conf_name).decode())
    for string in conf.splitlines():
        if string.startswith('!includedir'):
            conf = conf.replace(string, '')
            path = quote(string.split()[1])
            cfgs = ssh.execute_show('ls {}'.format(path)).split()
            for cfg in cfgs:
                conf += get_config(os.path.join(path, cfg))
    return conf


def clear_config(conf):
    return '\n'.join([s.lstrip() for s in conf.splitlines()
                      if not s.lstrip().startswith('#') and
                         s.lstrip() != ''])
