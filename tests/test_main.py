import pytest
import sys
import os
if os.getcwd().endswith('tests'):
    os.chdir('..')
sys.path.append(os.getcwd())

from shutil import rmtree, copytree
from main import run_tests
from modules.database import init_database

def setup_module(module):
    if '.test_tmp' in os.listdir():
        rmtree('.test_tmp')
    copytree('.', '.test_tmp')
    os.chdir('.test_tmp')
    init_database()

def teardown_module(module):
    os.chdir('..')
    if '.test_tmp' in os.listdir():
        rmtree('.test_tmp')

def test_run_tests():
    # TODO 2
    run_tests()
