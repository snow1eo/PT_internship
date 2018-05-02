#!/usr/bin/env python3

from modules.database import check_config, init_database, delete_database
from modules.reporting import generate_report
from modules.time import set_start_time, set_finish_time
from modules.testing import run_tests


if __name__ == '__main__':
    check_config()
    init_database()
    set_start_time()
    run_tests()
    set_finish_time()
    generate_report('sample_report.pdf')
    delete_database()
