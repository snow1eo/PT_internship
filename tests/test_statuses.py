from modules.statuses import get_status_name, Statuses


def test_get_status_name():
    for code in range(1, len(Statuses)+1):
        assert Statuses[get_status_name(code)].value == code
