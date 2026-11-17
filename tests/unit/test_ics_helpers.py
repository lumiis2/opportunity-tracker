from datetime import date, datetime, timedelta, timezone

import pytest

from src.core import CalendarEvent
from src.core.ics_generator import (
    build_event_lines,
    escape_text,
    event_signature,
    fold_ical_lines,
    format_utc_datetime,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (r"a\b", r"a\\b"),
        ("a;b", r"a\;b"),
        ("a,b", r"a\,b"),
        ("a\nb", r"a\nb"),
        ("a\rb", r"a\nb"),
        ("a\r\nb", r"a\nb"),
    ],
)
def test_escape_text_escapes_reserved_characters(value, expected):
    assert escape_text(value) == expected


def test_escape_text_preserves_plain_unicode_text():
    value = "Inscrições abertas em São Paulo"

    assert escape_text(value) == value


@pytest.mark.parametrize(
    ("stamp", "expected"),
    [
        (
            datetime(2027, 1, 1, 12, tzinfo=timezone.utc),
            "20270101T120000Z",
        ),
        (
            datetime(2027, 1, 1, 23, tzinfo=timezone(timedelta(hours=-3))),
            "20270102T020000Z",
        ),
        (
            datetime(2027, 1, 1, 12),
            "20270101T120000Z",
        ),
    ],
)
def test_format_utc_datetime_normalizes_supported_inputs(stamp, expected):
    assert format_utc_datetime(stamp) == expected


@pytest.mark.parametrize("length", [1, 74, 75])
def test_fold_ical_lines_preserves_lines_within_byte_limit(length):
    line = "A" * length

    assert fold_ical_lines([line]) == line


def test_fold_ical_lines_wraps_long_ascii_line_without_losing_content():
    line = "DESCRIPTION:" + "a" * 150

    result = fold_ical_lines([line])
    physical_lines = result.split("\r\n")

    assert len(physical_lines) > 1
    assert all(len(part.encode("utf-8")) <= 75 for part in physical_lines)
    assert all(part.startswith(" ") for part in physical_lines[1:])
    assert result.replace("\r\n ", "") == line


def test_fold_ical_lines_respects_utf8_byte_length():
    line = "DESCRIPTION:" + "Pesquisa em São Paulo. " * 10

    result = fold_ical_lines([line])
    physical_lines = result.split("\r\n")

    assert len(physical_lines) > 1
    assert all(len(part.encode("utf-8")) <= 75 for part in physical_lines)
    assert result.replace("\r\n ", "") == line


def test_build_event_lines_serializes_minimal_event():
    event = CalendarEvent(
        id="masters-example.application-deadline",
        title="Deadline",
        description="Example program",
        start_date=date(2027, 2, 1),
    )
    stamp = datetime(2027, 1, 1, 12, tzinfo=timezone.utc)

    result = build_event_lines(event, stamp)

    assert result == [
        "BEGIN:VEVENT",
        "UID:masters-example.application-deadline@opportunity-tracker",
        "DTSTAMP:20270101T120000Z",
        "SUMMARY:Deadline",
        "DESCRIPTION:Example program",
        "DTSTART;VALUE=DATE:20270201",
        "END:VEVENT",
    ]


def test_build_event_lines_includes_optional_event_details():
    event = CalendarEvent(
        id="masters-example.program-period",
        title="Program",
        description="Example program",
        start_date=date(2027, 2, 1),
        end_date=date(2027, 2, 3),
        url="https://example.org/apply",
        category="Scholarship",
    )
    stamp = datetime(2027, 1, 1, 12, tzinfo=timezone.utc)

    result = build_event_lines(event, stamp)

    assert "DTEND;VALUE=DATE:20270203" in result
    assert "URL:https://example.org/apply" in result
    assert "CATEGORIES:Scholarship" in result


def test_event_signature_ignores_generation_timestamp():
    first = ["SUMMARY:Deadline", "DTSTAMP:20270101T120000Z"]
    second = ["SUMMARY:Deadline", "DTSTAMP:20270102T120000Z"]

    assert event_signature(first) == ("SUMMARY:Deadline",)
    assert event_signature(second) == ("SUMMARY:Deadline",)


@pytest.mark.parametrize(
    ("original", "revised"),
    [
        ("SUMMARY:Deadline", "SUMMARY:New deadline"),
        ("DESCRIPTION:Old description", "DESCRIPTION:New description"),
        (
            "DTSTART;VALUE=DATE:20270101",
            "DTSTART;VALUE=DATE:20270102",
        ),
    ],
)
def test_event_signature_detects_changes_in_event_content(original, revised):
    assert event_signature([original]) != event_signature([revised])