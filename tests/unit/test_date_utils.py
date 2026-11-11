from datetime import date

import pytest

from src.utils.date_helpers import (
    clean_text,
    join_non_empty_lines,
    parse_exact_date,
    split_tags,
)


def test_clean_text_removes_surrounding_whitespace():
    assert clean_text("  Opportunity Tracker  ") == "Opportunity Tracker"


@pytest.mark.parametrize("value", [None, "", "   ", "nan", "None"])
def test_clean_text_normalizes_null_like_values(value):
    assert clean_text(value) == ""


def test_clean_text_preserves_numeric_zero():
    assert clean_text(0) == "0"


def test_split_tags_accepts_mixed_separators():
    assert split_tags("AI,ML;Python/Data Science|Research") == [
        "AI",
        "ML",
        "Python",
        "Data Science",
        "Research",
    ]


def test_split_tags_discards_empty_parts():
    assert split_tags(",  AI  ;; |  ML  , / ") == ["AI", "ML"]


@pytest.mark.parametrize("value", [None, "", "   ", "nan", "None"])
def test_split_tags_returns_empty_list_for_missing_input(value):
    assert split_tags(value) == []


def test_join_non_empty_lines_preserves_order():
    lines = ["", "Program: Example", "", "Funding: Free", ""]

    assert join_non_empty_lines(lines) == "Program: Example\nFunding: Free"


@pytest.mark.parametrize(
    "value",
    [
        "2026-11-25",
        "2026/11/25",
        "25/11/2026",
        "11/25/2026",
    ],
)
def test_parse_exact_date_accepts_supported_formats(value):
    assert parse_exact_date(value) == date(2026, 11, 25)


def test_parse_exact_date_extracts_iso_date_from_text():
    assert parse_exact_date("Deadline: 2026-11-06 (UTC)") == date(2026, 11, 6)
