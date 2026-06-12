from __future__ import annotations

from pathlib import Path

from ..domain.conference import Conference
from .common import first_month_from_text, parse_iso_date, read_rows, text_or_none


def parse_conferences(csv_path: Path) -> list[Conference]:
    rows = read_rows(csv_path)
    conferences: list[Conference] = []

    for row in rows:
        title = row.get("Title") or row.get("Conference") or row.get("Name") or row.get("Program") or "Conference"
        normalized = {
            "title": title,
            "organizer": row.get("Organizer") or row.get("Organization"),
            "country": row.get("Country"),
            "city": row.get("City"),
            "deadline": parse_iso_date(row.get("Deadline")),
            "expected_deadline_month": first_month_from_text([row.get("Deadline"), row.get("Expected Deadline Month")]),
            "website": row.get("Website") or row.get("Official Website"),
            "notes": row.get("Notes"),
            "raw": row,
        }
        conferences.append(Conference.model_validate(normalized))

    return conferences
