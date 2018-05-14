#!/usr/bin/env python3

from modules.audit import audit
from modules.database import init_scanning, set_finish_time
from modules.reporting import generate_report
from modules.testing import run_tests
from modules.transports import close_all_connections

if __name__ == '__main__':
    init_scanning()
    audit()
    run_tests()
    close_all_connections()
    set_finish_time()
    generate_report('sample_report.pdf')
