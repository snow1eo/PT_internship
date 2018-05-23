import sys
import traceback
from importlib import import_module

from modules.database import add_control, get_tests
from modules.statuses import Status


def run_tests():
    tests = get_tests()
    for id_, test in tests.items():
        try:
            test_mod = import_module('.' + test, package='scripts')
            status, msg = test_mod.main()
        except Exception:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            status, msg = Status.EXCEPTION, \
                ''.join(traceback.format_exception(*exc_info))
        add_control(id_, status, msg)
