import re
from importlib import import_module
import os

from modules.database import add_control
from modules.statuses import Statuses

def run_tests():
    tests = [test.strip('.py') for test in os.listdir('scripts')
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
