import time

_start_time_sec = None
_start_time = None
_finish_time_sec = None
_finish_time = None


def set_start_time():
    global _start_time_sec
    global _start_time
    if not _start_time:
        _start_time_sec = time.time()
        _start_time = time.ctime()


def get_start_time():
    return _start_time


def set_finish_time():
    global _finish_time_sec
    global _finish_time
    if not _finish_time:
        _finish_time_sec = time.time()
        _finish_time = time.ctime()


def get_finish_time():
    return _finish_time


def get_duration():
    full = int(_finish_time_sec - _start_time_sec)
    hours = full // 3600
    minutes = (full % 3600) // 60
    seconds = full % 60
    return '{:0>2}h:{:0>2}m:{:0>2}s'.format(hours, minutes, seconds)
