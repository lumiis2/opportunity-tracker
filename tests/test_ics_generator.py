from pathlib import Path
from datetime import date

import pytest

from src.core.ics_generator import generate_calendar
from src.core.calendar_event import CalendarEvent


def test_ics_generator_writes_file(tmp_path):
    events = [
        CalendarEvent(
            id="test-event",
            title="T1",
            description="D1",
            start_date=date(2026, 1, 1),
            url="https://example.org",
            tags=["x"],
        )
    ]

    out = tmp_path / "out.ics"
    generate_calendar(events, out, calendar_name="Test Calendar")
    assert out.exists()
    txt = out.read_text(encoding="utf-8")
    assert "BEGIN:VCALENDAR" in txt
    assert "BEGIN:VEVENT" in txt


def test_regeneration_preserves_existing_event_timestamp(tmp_path):
    event = CalendarEvent(
        "a-very-long-opportunity-identifier-that-requires-ical-line-folding.application-deadline",
        "Deadline",
        "description",
        date(2026, 1, 1),
    )
    output = tmp_path / "calendar.ics"
    generate_calendar([event], output, "Calendar")
    first = output.read_text(encoding="utf-8")
    generate_calendar([event], output, "Calendar")
    assert output.read_text(encoding="utf-8") == first


def test_event_revision_updates_timestamp_without_changing_uid(tmp_path):
    output = tmp_path / "calendar.ics"
    original = CalendarEvent("deadline", "Deadline", "old", date(2026, 1, 1))
    generate_calendar([original], output, "Calendar")
    contents = output.read_text(encoding="utf-8").replace(
        next(line for line in output.read_text(encoding="utf-8").splitlines() if line.startswith("DTSTAMP:")),
        "DTSTAMP:20000101T000000Z",
    )
    output.write_text(contents, encoding="utf-8")

    revised = CalendarEvent("deadline", "Deadline", "updated", date(2026, 2, 1))
    generate_calendar([revised], output, "Calendar")
    revised_contents = output.read_text(encoding="utf-8")

    assert "UID:deadline@opportunity-tracker" in revised_contents
    assert "DTSTAMP:20000101T000000Z" not in revised_contents


def test_duplicate_event_ids_are_rejected(tmp_path):
    events = [
        CalendarEvent("same-id", "First", "", date(2026, 1, 1)),
        CalendarEvent("same-id", "Second", "", date(2026, 2, 1)),
    ]

    with pytest.raises(ValueError, match="Duplicate event IDs: same-id"):
        generate_calendar(events, tmp_path / "calendar.ics", "Calendar")
