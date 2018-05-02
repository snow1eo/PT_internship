import os
import sys
from shutil import rmtree, copytree

import pytest

if os.getcwd().endswith('tests'):
    os.chdir('..')
sys.path.append(os.getcwd())
from modules.database import init_database
from modules.reporting import TEMPLATE_HTML, render, get_context, generate_report
from modules.time import set_start_time, set_finish_time


TEST_DIR = '.test_tmp'


def setup_module():
    if TEST_DIR in os.listdir():
        rmtree(TEST_DIR)
    copytree('.', TEST_DIR)
    os.chdir(TEST_DIR)
    init_database()


def teardown_module():
    os.chdir('..')
    if TEST_DIR in os.listdir():
        rmtree(TEST_DIR)


@pytest.mark.first
def test_get_context():
    assert isinstance(get_context(), dict)


def test_render():
    render(TEMPLATE_HTML, get_context())


def test_generate_report():
    set_start_time()
    set_finish_time()
    generate_report('test.pdf')
    if os.path.exists('test.pdf'):
        os.remove('test.pdf')
        assert True
    else:
        assert False
