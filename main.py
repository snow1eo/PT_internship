#!/usr/bin/env python3

from datetime import datetime

from modules.database import check_config, init_database, delete_database
from modules.reporting import generate_report
from modules.testing import run_tests


if __name__ == '__main__':
    check_config()
    init_database()
    start_time = datetime.now()
    run_tests()
    finish_time = datetime.now()
    generate_report('sample_report.pdf', start_time, finish_time)
    delete_database()
