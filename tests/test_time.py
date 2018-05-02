import pytest
import os
import sys

if os.getcwd().endswith('tests'):
    os.chdir('..')
sys.path.append(os.getcwd())
from modules.time import set_start_time, get_start_time, \
        set_finish_time, get_finish_time, get_duration


def test_start_time():
    set_start_time()
    assert get_start_time()


def test_finish_time():
    set_finish_time()
    assert get_finish_time()


@pytest.mark.last
def test_get_duration():
    assert get_duration()
