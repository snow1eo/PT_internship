import os
import sys

if os.getcwd().endswith('tests'):
    os.chdir('..')
sys.path.append(os.getcwd())
from modules.statuses import get_status_name


def test_get_status_name():
    for code in range(1,6):
        assert get_status_name(code)
