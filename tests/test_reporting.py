import os
from datetime import datetime

import pytest

from modules.database import init_database
from modules.reporting import TEMPLATE_HTML, render, get_context, generate_report


@pytest.mark.first
def test_get_context():
    assert isinstance(get_context(datetime.now(), datetime.now()), dict)


def test_render():
    render(TEMPLATE_HTML, get_context(datetime.now(), datetime.now()))


def test_generate_report(change_dir):
    init_database()
    generate_report('test.pdf', datetime.now(), datetime.now())
    assert os.path.exists('test.pdf')
    os.remove('test.pdf')
