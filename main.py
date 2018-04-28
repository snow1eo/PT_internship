#!/usr/bin/env python3

import importlib
import os
import re
import json
from modules.reporting import generate_report
from modules.database import *

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