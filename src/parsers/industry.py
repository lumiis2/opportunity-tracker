"""Parser for the Industry Opportunities dataset."""

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
    "Company",
    "Company Size",
    "Company Stage",
    "Headquarters",
    "Primary Focus",
    "Main Domains",
    "Tech Stack",
    "Work Model",
    "Internship Program",
    "International Internship",
    "New Grad / Early Career",
    "Typical Recruiting Season",
    "Applications Open",
    "Application Deadline",
    "Expected Open Month",
    "Expected Deadline Month",
    "Date Status",
    "Entry-Level Roles",
    "Sponsorship Available",
    "AI/ML Fit Score (1-10)",
    "Technical Reputation Score (1-10)",
    "Growth Score (1-10)",
    "Priority",
    "Careers Page",
    "Application Portal",
    "Notes",
]


class IndustryParser:
    """Parse industry opportunity rows into calendar events."""

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
        company = clean_text(row.get("Company"))
        category = clean_text(row.get("Category")) or None
        program_name = company
        if not program_name:
            return []

        title_base = f"{program_name}".strip()
        description = self._build_description(row)
        url = clean_text(row.get("Careers Page")) or clean_text(row.get("Application Portal")) or None

        tags = []
        tags.extend(split_tags(row.get("Primary Focus")))
        tags.extend(split_tags(row.get("Main Domains")))

        events: list[CalendarEvent] = []

        app_open = parse_exact_date(row.get("Applications Open"))
        if app_open:
            events.append(
                self._event(
                    title=f"Applications Open — {title_base}",
                    start_date=app_open,
                    description=description,
                    url=url,
                    category=category,
                    tags=tags,
                )
            )

        app_deadline = parse_exact_date(row.get("Application Deadline"))
        if app_deadline:
            events.append(
                self._event(
                    title=f"Application Deadline — {title_base}",
                    start_date=app_deadline,
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
                    title=f"Expected Applications Open — {title_base}",
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
            ("Company", "Company"),
            ("Category", "Category"),
            ("Company Size", "Company Size"),
            ("Company Stage", "Company Stage"),
            ("Headquarters", "Headquarters"),
            ("Primary Focus", "Primary Focus"),
            ("Main Domains", "Main Domains"),
            ("Tech Stack", "Tech Stack"),
            ("Work Model", "Work Model"),
            ("Internship Program", "Internship Program"),
            ("International Internship", "International Internship"),
            ("New Grad / Early Career", "New Grad / Early Career"),
            ("Typical Recruiting Season", "Typical Recruiting Season"),
            ("Entry-Level Roles", "Entry-Level Roles"),
            ("Sponsorship Available", "Sponsorship Available"),
            ("AI/ML Fit Score (1-10)", "AI/ML Fit Score (1-10)"),
            ("Technical Reputation Score (1-10)", "Technical Reputation Score (1-10)"),
            ("Growth Score (1-10)", "Growth Score (1-10)"),
            ("Priority", "Priority"),
            ("Notes", "Notes"),
        ]

        for key, label in fields:
            value = clean_text(row.get(key))
            if value:
                lines.append(f"{label}: {value}")

        return join_non_empty_lines(lines)


def parse(csv_path: str | Path) -> list[CalendarEvent]:
    return IndustryParser().parse(csv_path)
