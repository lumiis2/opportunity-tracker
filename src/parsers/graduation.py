"""Parser for the Graduation Opportunities dataset."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import csv

from src.core.calendar_event import CalendarEvent
from src.utils.date_helpers import (
    clean_text,
    join_non_empty_lines,
    parse_exact_date,
    parse_month_start,
    split_tags,
)


EXPECTED_COLUMNS = [
    "Category",
    "Subcategory",
    "Program",
    "Organization",
    "Host Institution",
    "Country",
    "Target Audience",
    "Funding",
    "Funding Details",
    "Supervisor Match",
    "Duration",
    "Application Open",
    "Application Deadline",
    "Expected Open Month",
    "Expected Deadline Month",
    "Date Status",
    "Deadline Confidence",
    "Application Effort",
    "Prestige Score (1-10)",
    "Funding Score (1-10)",
    "AI/ML Fit Score (1-10)",
    "Application Portal",
    "Required Documents",
    "Tags",
    "Official Website",
    "Notes",
]


class GraduationParser:
    """Parse graduation opportunities rows into calendar events."""

    def parse(self, csv_path: str | Path) -> list[CalendarEvent]:
        path = Path(csv_path)
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            self._validate_columns(reader.fieldnames)

            events: list[CalendarEvent] = []
            for row in reader:
                events.extend(self._parse_row(row))
            return events

    def _validate_columns(self, fieldnames: list[str] | None) -> None:
        if not fieldnames:
            raise ValueError("CSV file has no header row")

        missing = [name for name in EXPECTED_COLUMNS if name not in fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

    def _parse_row(self, row: dict[str, str]) -> list[CalendarEvent]:
        program = clean_text(row.get("Program"))
        if not program:
            raise ValueError("Missing Program value in row")

        description = self._build_description(row)
        category = clean_text(row.get("Category")) or None
        url = clean_text(row.get("Official Website")) or clean_text(row.get("Application Portal")) or None
        tags = split_tags(row.get("Tags"))

        events: list[CalendarEvent] = []

        application_open = parse_exact_date(row.get("Application Open"))
        if application_open:
            events.append(
                self._event(
                    title=f"Application Opens — {program}",
                    start_date=application_open,
                    description=description,
                    url=url,
                    category=category,
                    tags=tags,
                )
            )

        application_deadline = parse_exact_date(row.get("Application Deadline"))
        if application_deadline:
            events.append(
                self._event(
                    title=f"Application Deadline — {program}",
                    start_date=application_deadline,
                    description=description,
                    url=url,
                    category=category,
                    tags=tags,
                )
            )

        expected_open = parse_month_start(row.get("Expected Open Month"))
        if expected_open:
            events.append(
                self._event(
                    title=f"Expected Applications Open — {program}",
                    start_date=expected_open,
                    description=description,
                    url=url,
                    category=category,
                    tags=tags,
                )
            )

        return events

    def _event(
        self,
        *,
        title: str,
        start_date: date,
        description: str,
        url: str | None,
        category: str | None,
        tags: list[str],
    ) -> CalendarEvent:
        return CalendarEvent(
            title=title,
            description=description,
            start_date=start_date,
            url=url,
            category=category,
            tags=tags,
        )

    def _build_description(self, row: dict[str, str]) -> str:
        lines = []
        fields = [
            ("Program", "Program"),
            ("Organization", "Organization"),
            ("Host Institution", "Host Institution"),
            ("Country", "Country"),
            ("Target Audience", "Target Audience"),
            ("Funding", "Funding"),
            ("Funding Details", "Funding Details"),
            ("Supervisor Match", "Supervisor Match"),
            ("Duration", "Duration"),
            ("Application Effort", "Application Effort"),
            ("Required Documents", "Required Documents"),
            ("Tags", "Tags"),
            ("Official Website", "Official Website"),
            ("Notes", "Notes"),
        ]

        for key, label in fields:
            value = clean_text(row.get(key))
            if value:
                lines.append(f"{label}: {value}")

        return join_non_empty_lines(lines)


def parse(csv_path: str | Path) -> list[CalendarEvent]:
    """Parse a graduation CSV into calendar events."""

    return GraduationParser().parse(csv_path)
