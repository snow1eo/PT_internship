import pytest
import sys, os
from shutil import rmtree, copytree
import json
if os.getcwd().endswith('tests'):
    os.chdir('..')
sys.path.append(os.getcwd())
from main import ConfigError, check_config, run_tests

def setup_module(module):
    if '.test_tmp' in os.listdir():
        rmtree('.test_tmp')
    copytree('.', '.test_tmp')
    os.chdir('.test_tmp')

def teardown_module(module):
    os.chdir('..')
    if '.test_tmp' in os.listdir():
        rmtree('.test_tmp')

@pytest.mark.first
def test_check_config():
    # TODO (somwhere. Probably)
    pass

def test_run_tests():
    # TODO 2
    pass