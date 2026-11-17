from datetime import date

import pytest

from src.utils.date_helpers import (
    parse_exact_date,
    parse_month_start,
    resolve_date,
    resolve_window,
)


@pytest.mark.parametrize(
    "value",
    ["2026-02-30", "2026-13-01", "2026-01-32", "2026-00-10"],
)
def test_parse_exact_date_rejects_impossible_dates(value):
    assert parse_exact_date(value) is None


@pytest.mark.parametrize("value", [None, "", "TBD", "N/A"])
def test_parse_exact_date_returns_none_for_unknown_values(value):
    assert parse_exact_date(value) is None


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2028-02-29", date(2028, 2, 29)),
        ("2027-02-29", None),
    ],
)
def test_parse_exact_date_respects_leap_years(value, expected):
    assert parse_exact_date(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("January 2027", date(2027, 1, 1)),
        ("july 2027", date(2027, 7, 1)),
        ("DECEMBER 2027", date(2027, 12, 1)),
    ],
)
def test_parse_month_start_accepts_english_month_names(value, expected):
    assert parse_month_start(value) == expected


def test_parse_month_start_uses_fallback_year():
    assert parse_month_start("November", fallback_year=2030) == date(
        2030, 11, 1
    )


def test_parse_month_start_prefers_explicit_year():
    assert parse_month_start("November 2027", fallback_year=2030) == date(
        2027, 11, 1
    )


@pytest.mark.parametrize("value", [None, "", "TBD", "Unknown 2027"])
def test_parse_month_start_rejects_unknown_month(value):
    assert parse_month_start(value, fallback_year=2027) is None


def test_resolve_date_prefers_month_from_primary_value():
    result = resolve_date("September 2027", "October 2027")

    assert result is not None
    assert result.value == date(2027, 9, 1)
    assert result.estimated is True


def test_resolve_date_uses_estimate_when_exact_date_is_invalid():
    result = resolve_date("2027-02-30", "March 2027")

    assert result is not None
    assert result.value == date(2027, 3, 1)
    assert result.estimated is True


def test_resolve_window_does_not_shift_confirmed_deadline_year():
    _, deadline = resolve_window(
        open_value="2027-10-01",
        deadline_value="2027-01-15",
    )

    assert deadline is not None
    assert deadline.value == date(2027, 1, 15)
    assert deadline.estimated is False