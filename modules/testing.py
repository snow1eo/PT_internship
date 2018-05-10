from importlib import import_module

from modules.database import add_control, get_tests
from modules.statuses import Status


def run_tests():
    tests = get_tests()
    for id_, test in tests.items():
        try:
            test_mod = import_module('.'+test, package='scripts')
            status, err = test_mod.main()
        except Exception as e_info:
            status, err = Status.EXCEPTION, e_info
        add_control(id_, status, err)
