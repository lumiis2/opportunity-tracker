from pathlib import Path
from datetime import date

from src.core.ics_generator import build_uid, generate_calendar
from src.core.calendar_event import CalendarEvent


def test_ics_generator_writes_file(tmp_path):
    events = [
        CalendarEvent(
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


def test_uid_survives_description_and_tag_edits():
    original = CalendarEvent("Deadline", "old", date(2026, 1, 1), url="https://example.org", tags=["old"])
    edited = CalendarEvent("Deadline", "new", date(2026, 1, 1), url="https://example.org", tags=["new"])
    assert build_uid(original) == build_uid(edited)


def test_regeneration_preserves_existing_event_timestamp(tmp_path):
    event = CalendarEvent("Deadline", "description", date(2026, 1, 1))
    output = tmp_path / "calendar.ics"
    generate_calendar([event], output, "Calendar")
    first = output.read_text(encoding="utf-8")
    generate_calendar([event], output, "Calendar")
    assert output.read_text(encoding="utf-8") == first
