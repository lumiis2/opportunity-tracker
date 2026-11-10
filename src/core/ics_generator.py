"""Generic ICS calendar generation utilities."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import re
import uuid

from src.core.calendar_event import CalendarEvent


DEFAULT_PRODUCT_ID = "-//Opportunity Tracker//EN"
DEFAULT_TIMEZONE = "UTC"


def generate_calendar(
    events: list[CalendarEvent],
    output_path: Path,
    calendar_name: str,
) -> None:
    """Write a valid RFC5545 .ics calendar file for the provided events."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    existing_stamps = read_existing_stamps(output_path)

    lines: list[str] = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:{DEFAULT_PRODUCT_ID}",
        f"CALSCALE:GREGORIAN",
        f"METHOD:PUBLISH",
        f"X-WR-CALNAME:{escape_text(calendar_name)}",
        f"X-WR-TIMEZONE:{DEFAULT_TIMEZONE}",
    ]

    for event in events:
        uid = build_uid(event)
        lines.extend(build_event_lines(event, existing_stamps.get(uid, now)))

    lines.append("END:VCALENDAR")

    output_path.write_text(fold_ical_lines(lines) + "\r\n", encoding="utf-8")


def build_event_lines(event: CalendarEvent, stamp: datetime) -> list[str]:
    """Build the VEVENT block for one calendar event."""

    uid = build_uid(event)
    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{format_utc_datetime(stamp)}",
        f"SUMMARY:{escape_text(event.title)}",
        f"DESCRIPTION:{escape_text(event.description)}",
        f"DTSTART;VALUE=DATE:{event.start_date.strftime('%Y%m%d')}",
    ]

    if event.end_date is not None:
        lines.append(f"DTEND;VALUE=DATE:{event.end_date.strftime('%Y%m%d')}")

    if event.url:
        lines.append(f"URL:{escape_text(event.url)}")

    categories: list[str] = []
    if event.category:
        categories.append(event.category)
    categories.extend(event.tags)
    categories = [item for item in categories if item]
    if categories:
        lines.append(f"CATEGORIES:{escape_text(','.join(categories))}")

    lines.append("END:VEVENT")
    return lines


def read_existing_stamps(path: Path) -> dict[str, datetime]:
    """Keep DTSTAMP stable for events whose UID already exists."""

    if not path.exists():
        return {}
    contents = path.read_text(encoding="utf-8")
    stamps: dict[str, datetime] = {}
    for block in re.findall(r"BEGIN:VEVENT\r?\n(.*?)\r?\nEND:VEVENT", contents, re.DOTALL):
        uid_match = re.search(r"^UID:(.+)$", block, re.MULTILINE)
        stamp_match = re.search(r"^DTSTAMP:(\d{8}T\d{6}Z)\r?$", block, re.MULTILINE)
        if not uid_match or not stamp_match:
            continue
        try:
            stamps[uid_match.group(1).rstrip("\r")] = datetime.strptime(
                stamp_match.group(1), "%Y%m%dT%H%M%SZ"
            ).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return stamps


def build_uid(event: CalendarEvent) -> str:
    """Generate a stable, unique identifier for an event."""

    seed = "|".join(
        [
            event.title,
            event.start_date.isoformat(),
            event.end_date.isoformat() if event.end_date else "",
            event.url or "",
        ]
    )
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()
    return f"{uuid.UUID(digest[:32])}@opportunity-tracker"


def format_utc_datetime(value: datetime) -> str:
    """Format a datetime in the UTC timestamp form required by ICS."""

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    return value.strftime("%Y%m%dT%H%M%SZ")


def escape_text(value: str) -> str:
    """Escape text per RFC5545."""

    return (
        value.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
        .replace("\r", "\\n")
    )


def fold_ical_lines(lines: list[str]) -> str:
    """Fold lines to keep them compatible with ICS readers."""

    folded: list[str] = []
    for line in lines:
        encoded = line.encode("utf-8")
        if len(encoded) <= 75:
            folded.append(line)
            continue

        current = ""
        current_len = 0
        for char in line:
            char_bytes = char.encode("utf-8")
            if current_len + len(char_bytes) > 75:
                folded.append(current)
                current = " " + char
                current_len = len(current.encode("utf-8"))
            else:
                current += char
                current_len += len(char_bytes)
        if current:
            folded.append(current)

    return "\r\n".join(folded)
