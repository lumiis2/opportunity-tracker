"""Parser for the Conferences dataset."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import csv
import re

from src.core.calendar_event import CalendarEvent
from src.utils.date_helpers import (
    clean_text,
    join_non_empty_lines,
    parse_exact_date,
    parse_month_start,
    split_tags,
)


EXPECTED_COLUMNS = [
    "Conference Name",
    "Area",
    "Tier (A*, A, B, C)",
    "Country",
    "Region (US / Europe / China / Brazil / Other)",
    "Organizer / Association",
    "Focus Areas",
    "Submission Deadline (Exact or Empty if unknown)",
    "Notification Date",
    "Conference Date Range",
    "Expected Submission Month",
    "Expected Conference Month",
    "Date Status (Confirmed / Estimated / Rolling / Unknown)",
    "Location Type (In-person / Virtual / Hybrid)",
    "Acceptance Rate (if known, else blank)",
    "Website",
    "Submission Portal",
    "Research Tags",
    "Industry Relevance Score (1-10)",
    "Research Impact Score (1-10)",
    "Prestige Score (1-10)",
    "Priority (P0 / P1 / P2)",
    "Notes",
]


class ConferenceParser:
    """Parse conference rows into calendar events."""

    def parse(self, csv_path: str | Path) -> list[CalendarEvent]:
        path = Path(csv_path)
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            # do not strictly require every possible header; validate minimal presence
            if not reader.fieldnames:
                raise ValueError("CSV file has no header row")

            events: list[CalendarEvent] = []
            for row in reader:
                events.extend(self._parse_row(row))
            return events

    def _parse_row(self, row: dict[str, str]) -> list[CalendarEvent]:
        name = clean_text(row.get("Conference Name"))
        if not name:
            return []

        area = clean_text(row.get("Area"))
        research_tags = split_tags(row.get("Research Tags"))
        tags = []
        if area:
            tags.append(area)
        tags.extend(research_tags)

        description = self._build_description(row)
        url = clean_text(row.get("Submission Portal")) or clean_text(row.get("Website")) or None

        events: list[CalendarEvent] = []

        # Submission deadline (exact)
        sub_dead = parse_exact_date(row.get("Submission Deadline (Exact or Empty if unknown)"))
        if sub_dead:
            events.append(
                self._event(
                    title=f"Paper Submission Deadline — {name}",
                    start_date=sub_dead,
                    description=description,
                    url=url,
                    category=area or None,
                    tags=tags,
                )
            )

        # Expected submission month
        expected_sub = parse_month_start(row.get("Expected Submission Month"))
        if expected_sub:
            events.append(
                self._event(
                    title=f"Expected Paper Submission — {name}",
                    start_date=expected_sub,
                    description=description,
                    url=url,
                    category=area or None,
                    tags=tags,
                )
            )

        # Notification date
        notif = parse_exact_date(row.get("Notification Date"))
        if notif:
            events.append(
                self._event(
                    title=f"Acceptance Notification — {name}",
                    start_date=notif,
                    description=description,
                    url=url,
                    category=area or None,
                    tags=tags,
                )
            )

        # Conference date range: format "YYYY-MM-DD to YYYY-MM-DD"
        rng = clean_text(row.get("Conference Date Range"))
        if rng:
            m = re.search(r"(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})", rng)
            if m:
                start = parse_exact_date(m.group(1))
                end = parse_exact_date(m.group(2))
                if start and end:
                    events.append(
                        ConferenceParser()._event(
                            title=f"{name} Conference",
                            start_date=start,
                            end_date=end,
                            description=description,
                            url=url,
                            category=area or None,
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
        end_date: date | None = None,
    ) -> CalendarEvent:
        return CalendarEvent(
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            url=url,
            category=category,
            tags=tags,
        )

    def _build_description(self, row: dict[str, str]) -> str:
        fields = [
            ("Conference Name", "Conference Name"),
            ("Area", "Area"),
            ("Tier (A*, A, B, C)", "Tier"),
            ("Country", "Country"),
            ("Region (US / Europe / China / Brazil / Other)", "Region"),
            ("Organizer / Association", "Organizer / Association"),
            ("Focus Areas", "Focus Areas"),
            ("Date Status (Confirmed / Estimated / Rolling / Unknown)", "Date Status"),
            ("Location Type (In-person / Virtual / Hybrid)", "Location Type"),
            ("Acceptance Rate (if known, else blank)", "Acceptance Rate"),
            ("Research Tags", "Research Tags"),
            ("Industry Relevance Score (1-10)", "Industry Relevance Score"),
            ("Research Impact Score (1-10)", "Research Impact Score"),
            ("Prestige Score (1-10)", "Prestige Score"),
            ("Priority (P0 / P1 / P2)", "Priority"),
            ("Notes", "Notes"),
        ]

        lines: list[str] = []
        for key, label in fields:
            val = clean_text(row.get(key))
            if val:
                lines.append(f"{label}: {val}")

        return join_non_empty_lines(lines)


def parse(csv_path: str | Path) -> list[CalendarEvent]:
    return ConferenceParser().parse(csv_path)
