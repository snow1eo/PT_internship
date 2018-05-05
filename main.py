#!/usr/bin/env python3

from modules.database import init_scanning, set_finish_time
from modules.reporting import generate_report
from modules.testing import run_tests

if __name__ == '__main__':
    init_scanning()
    run_tests()
    set_finish_time()
    generate_report('sample_report.pdf')
