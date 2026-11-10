from datetime import date

from src.utils.date_helpers import resolve_date, resolve_window


def test_exact_date_wins_over_expected_month():
    resolved = resolve_date("2027-09-16", "October 2027")

    assert resolved is not None
    assert resolved.value == date(2027, 9, 16)
    assert resolved.estimated is False


def test_month_is_marked_as_estimated():
    resolved = resolve_date("", "September", fallback_year=2027)

    assert resolved is not None
    assert resolved.value == date(2027, 9, 1)
    assert resolved.estimated is True


def test_estimated_deadline_can_cross_into_next_year():
    opening, deadline = resolve_window(
        open_value="",
        deadline_value="",
        expected_open="October 2027",
        expected_deadline="January",
    )

    assert opening is not None
    assert deadline is not None
    assert opening.value == date(2027, 10, 1)
    assert deadline.value == date(2028, 1, 1)


def test_empty_window_has_no_dates():
    assert resolve_window(open_value="", deadline_value="") == (None, None)
