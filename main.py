#!/usr/bin/env python3

import importlib
import os
import re
import json
from modules.reporting import generate_report
from modules.database import init_database, delete_database, add_control

class ConfigError(Exception):
    pass

def check_config():
    if 'controls.json' not in os.listdir('./'):
        raise ConfigError("controls.json doesn't exist")
    test_nums = [int(re.findall(r'\d+', test)[0]) for test in os.listdir('scripts')\
                            if re.match(r'\d+_.+\.py', test)]
    if len(test_nums) != len(set(test_nums)):
        raise ConfigError('duplicate test numbers')
    with open('controls.json') as f:
        cfg_nums = [int(ctrl[0]) for ctrl in json.load(f)]
    if len(cfg_nums) != len(set(cfg_nums)):
        raise ConfigError('duplicate items')
    if not set(test_nums).issubset(set(cfg_nums)):
        raise ConfigError("config doesn't match scripts")

def run_tests():
    tests = [test.strip('.py') for test in os.listdir('scripts')\
                            if re.match(r'\d+_.+\.py', test)]

    for test in tests:
        ctrl_id = re.findall(r'\d+', test)[0]
        try:
            test_mod = importlib.import_module('.'+test, package = 'scripts')
            status = test_mod.main()
        except Exception as e_info:
            print('ERROR: {}'.format(e_info))
            status = 5
        add_control(ctrl_id, status)

if __name__ == '__main__':
    check_config()
    init_database()
    run_tests()
    generate_report()
    delete_database()