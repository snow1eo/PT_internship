#!/usr/bin/env python3

import importlib
# import pathlib
import json
import os
import re

from modules.database import check_config, init_database, delete_database, add_control
from modules.reporting import generate_report

with open('statuses.json') as f:
    statuses = json.load(f)


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
            status = statuses['EXCEPTION']['code']
        add_control(ctrl_id, status)


if __name__ == '__main__':
    check_config()
    init_database()
    run_tests()
    generate_report()
    delete_database()
