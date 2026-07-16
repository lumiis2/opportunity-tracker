"""Parser for the AI/ML Research & Fellowships dataset."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import csv
import re

from src.core.calendar_event import CalendarEvent
from src.utils.date_helpers import clean_text, join_non_empty_lines, parse_exact_date, parse_month_start


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
    "Official Website",
    "Notes",
]

_MARKDOWN_LINK = re.compile(r"^\[([^]]+)]\((https?://[^)]+)\)$")


def _link_label(value: object) -> str:
    text = clean_text(value)
    match = _MARKDOWN_LINK.match(text)
    return match.group(1) if match else text


def _link_url(value: object) -> str:
    text = clean_text(value)
    match = _MARKDOWN_LINK.match(text)
    return match.group(2) if match else text


class AiMlResearchFellowshipsParser:
    """Turn program application dates into normalized calendar events."""

    def parse(self, csv_path: str | Path) -> list[CalendarEvent]:
        with Path(csv_path).open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            self._validate_columns(reader.fieldnames)
            return [event for row in reader for event in self._parse_row(row)]

    @staticmethod
    def _validate_columns(fieldnames: list[str] | None) -> None:
        if not fieldnames:
            raise ValueError("CSV file has no header row")
        missing = [column for column in EXPECTED_COLUMNS if column not in fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

    def _parse_row(self, row: dict[str, str]) -> list[CalendarEvent]:
        program = _link_label(row.get("Program"))
        if not program:
            return []

        category = clean_text(row.get("Category")) or None
        subcategory = clean_text(row.get("Subcategory"))
        tags = [subcategory] if subcategory else []
        description = self._build_description(row)
        url = _link_url(row.get("Official Website")) or None
        events: list[CalendarEvent] = []

        application_open = parse_exact_date(row.get("Application Open"))
        deadline = parse_exact_date(row.get("Application Deadline"))

        if application_open:
            events.append(self._event(f"Applications Open — {program}", application_open, description, url, category, tags))
        if deadline:
            events.append(self._event(f"Application Deadline — {program}", deadline, description, url, category, tags))

        expected_open = None
        if not application_open:
            expected_open = parse_month_start(row.get("Application Open")) or parse_month_start(
                row.get("Expected Open Month")
            )
            if expected_open:
                events.append(self._event(f"Expected Applications Open — {program}", expected_open, description, url, category, tags))

        if not deadline:
            fallback_year = expected_open.year if expected_open else None
            expected_deadline = parse_month_start(
                row.get("Application Deadline"), fallback_year=fallback_year
            ) or parse_month_start(
                row.get("Expected Deadline Month"), fallback_year=fallback_year
            )
            if expected_deadline:
                if expected_open and expected_deadline < expected_open:
                    expected_deadline = expected_deadline.replace(year=expected_deadline.year + 1)
                events.append(self._event(f"Expected Application Deadline — {program}", expected_deadline, description, url, category, tags))

        if not events and self._is_continuous(row):
            events.append(
                self._event(
                    f"Applications Open Continuously — {program}",
                    date(date.today().year, 1, 1),
                    description,
                    url,
                    category,
                    tags,
                )
            )

        return events

    @staticmethod
    def _is_continuous(row: dict[str, str]) -> bool:
        values = (
            row.get("Application Open"),
            row.get("Application Deadline"),
            row.get("Expected Open Month"),
            row.get("Expected Deadline Month"),
        )
        return any(
            clean_text(value).lower() in {"open", "always open", "continuous", "rolling"}
            for value in values
        )

    @staticmethod
    def _event(
        title: str,
        start_date: date,
        description: str,
        url: str | None,
        category: str | None,
        tags: list[str],
    ) -> CalendarEvent:
        return CalendarEvent(
            title=title,
            start_date=start_date,
            description=description,
            url=url,
            category=category,
            tags=tags,
        )

    @staticmethod
    def _build_description(row: dict[str, str]) -> str:
        excluded = {
            "Application Open",
            "Application Deadline",
            "Expected Open Month",
            "Expected Deadline Month",
            "Official Website",
        }
        lines = []
        for column in EXPECTED_COLUMNS:
            if column in excluded:
                continue
            value = _link_label(row.get(column))
            if value:
                lines.append(f"{column}: {value}")
        return join_non_empty_lines(lines)


def parse(csv_path: str | Path) -> list[CalendarEvent]:
    return AiMlResearchFellowshipsParser().parse(csv_path)
