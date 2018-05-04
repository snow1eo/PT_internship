from importlib import import_module

from modules.database import add_control, get_tests
from modules.statuses import Status
import scripts  # for Windows


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
