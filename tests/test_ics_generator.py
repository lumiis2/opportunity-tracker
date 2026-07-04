from pathlib import Path
from datetime import date

from src.core.ics_generator import generate_calendar
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
