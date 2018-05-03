import os
import re
from importlib import import_module

from modules.database import add_control, check_config
from modules.statuses import Status
import scripts  # for Windows


def get_tests():
    check_config()
    return {
                re.findall(r'\d+', test)[0]: test.strip('.py')
                for test in os.listdir('scripts')
                if re.match(r'\d+_.+\.py', test)
           }


def run_tests():
    tests = get_tests()
    for id_, test in tests.items():
        try:
            test_mod = import_module('.'+test, package='scripts')
            status = test_mod.main()
        except Exception as e_info:
            print('ERROR: {}'.format(e_info))
            status = Status.EXCEPTION
        add_control(id_, status)
