#!/usr/bin/env python3

import re
from importlib import import_module
from os import listdir

from modules.database import add_control, check_config, \
    init_database, delete_database
from modules.reporting import generate_report
from modules.statuses import Statuses
from modules.time import set_start_time, set_finish_time


def run_tests():
    tests = [test.strip('.py') for test in listdir('scripts')
             if re.match(r'\d+_.+\.py', test)]
    for test in tests:
        ctrl_id = re.findall(r'\d+', test)[0]
        try:
            test_mod = import_module('.'+test, package='scripts')
            status = test_mod.main()
        except Exception as e_info:
            print('ERROR: {}'.format(e_info))
            status = Statuses.EXCEPTION.value
        add_control(ctrl_id, status)


if __name__ == '__main__':
    check_config()
    init_database()
    set_start_time()
    run_tests()
    set_finish_time()
    generate_report('sample_report.pdf')
    delete_database()
