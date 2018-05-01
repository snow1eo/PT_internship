import os
import sys
from shutil import rmtree, copytree

if os.getcwd().endswith('tests'):
    os.chdir('..')
sys.path.append(os.getcwd())
from main import run_tests
from modules.database import init_database


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


def test_run_tests():
    # TODO 2
    run_tests()
