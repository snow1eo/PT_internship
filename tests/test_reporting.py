import os
from shutil import rmtree, copytree
from datetime import datetime

import pytest

from modules.database import init_database
from modules.reporting import TEMPLATE_HTML, render, get_context, generate_report

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
    assert isinstance(get_context(datetime.now(), datetime.now()), dict)


def test_render():
    render(TEMPLATE_HTML, get_context(datetime.now(), datetime.now()))


def test_generate_report():
    generate_report('test.pdf', datetime.now(), datetime.now())
    assert os.path.exists('test.pdf'):
    os.remove('test.pdf')
