#!/usr/bin/env python3

import importlib
# import pathlib
import os
import re

import modules.database as db
from modules.reporting import generate_report
from modules.time import set_start_time, set_finish_time
from modules.statuses import Statuses


def run_tests():
    tests = [test.strip('.py') for test in os.listdir('scripts')
             if re.match(r'\d+_.+\.py', test)]
    # Тут только такой вариант заставил работать, и он мне вообще не нравится ><
    # tests = map(lambda x:str(x).strip('.py').lstrip('scripts'), pathlib.Path('scripts').glob(r'[0-9][0-9][0-9]_*.py'))
    for test in tests:
        ctrl_id = re.findall(r'\d+', test)[0]
        try:
            test_mod = importlib.import_module('.'+test, package='scripts')
            status = test_mod.main()
        except Exception as e_info:
            print('ERROR: {}'.format(e_info))
            status = Statuses.EXCEPTION.value
        db.add_control(ctrl_id, status)


if __name__ == '__main__':
    db.check_config()
    db.init_database()
    set_start_time()
    run_tests()
    set_finish_time()
    generate_report()
    db.delete_database()
