import re

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
            ssh.execute_show('ps -eo pid,euser,comm').split('\n')[1:-1]]
