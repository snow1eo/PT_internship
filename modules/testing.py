import sys
import traceback
from importlib import import_module

from modules.database import add_control, get_tests
from modules.statuses import Status


def run_tests():
    tests = get_tests()
    for id_, test in tests.items():
        try:
            print("Test {}...".format(id_), end='')
            test_mod = import_module('.' + test, package='scripts')
            status, msg = test_mod.main()
            print('DONE')
        except Exception:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            status, msg = Status.EXCEPTION, traceback.format_exception(*exc_info)[-1]
        add_control(id_, status, msg)
