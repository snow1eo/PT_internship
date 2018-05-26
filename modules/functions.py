import os
import re
from hashlib import sha1
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


def mysql_hash(password):
    pass1 = sha1(password.encode()).digest()
    pass2 = sha1(pass1).hexdigest()
    return '*' + pass2.upper()

# SSH


def get_processes(ssh):
    return [x.split() for x in
            ssh.execute_show('ps -eo pid,euser,comm').splitlines()[1:-1]]


def get_config(ssh, conf_name):
    conf = clear_config(ssh.get_file(conf_name).decode())
    for string in conf.splitlines():
        if string.startswith('!includedir'):
            conf = conf.replace(string + '\n', '')
            path = string.split()[1]
            cfgs = ssh.execute_show('ls {}'.format(path)).split()
            for cfg in cfgs:
                conf += get_config(ssh, quote(os.path.join(path, cfg)))
    return conf


def clear_config(conf):
    return '\n'.join([s.lstrip() for s in conf.splitlines()
                      if not s.lstrip().startswith('#') and
                         s.lstrip() != ''])


def check_permissions(required, current):
    required = required.copy()
    if ~int(required.pop('permissions'), 8) & int(current.pop('permissions'), 8):
        return False
    required.pop('filename')
    required.setdefault('owner', current['owner'])
    required.setdefault('group', current['group'])
    return required == current


def get_permissions(ssh, filename):
    data = ssh.execute_show(
        'stat --printf="%a %U %G" {}'.format(quote(filename))).split()
    return dict(
        permissions=data[0],
        owner=data[1],
        group=data[2])


def make_message_compl(curr):
    msg = "{filename}:{permissions}"
    if 'owner' in curr:
        msg += '::{owner}'
    if 'group' in curr:
        msg += ':{group}'
    return msg.format(**curr)


def make_message_not_compl(req, curr):
    if 'onwer' in curr and 'group' in curr:
        msg = "{filename}:{permissions}::{owner}:{group} != \
            {c_permission}::{c_owner}:{c_group}"
        return msg.format(**req,
                          c_permission=curr['permissions'],
                          c_owner=curr['owner'],
                          c_group=curr['group'])
    else:
        msg = "{filename}:{permissions} != {c_permission}"
        return msg.format(**req, c_permission=curr['permissions'])
