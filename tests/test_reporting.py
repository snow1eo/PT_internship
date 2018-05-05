import os

import pytest

from modules.database import init_database
from modules.reporting import TEMPLATE_HTML, render, get_context, generate_report


@pytest.mark.first
def test_get_context(change_dir, create_new_database):
    assert isinstance(get_context(), dict)


def test_render(change_dir, create_new_database):
    render(TEMPLATE_HTML, get_context())


def test_generate_report(change_dir, create_new_database):
    init_database()
    generate_report('test.pdf')
    assert os.path.exists('test.pdf')
    os.remove('test.pdf')
