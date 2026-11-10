"""Parser for the Master Programs dataset."""

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
from src.utils.identifiers import event_id, opportunity_id


EXPECTED_COLUMNS = [
    "University",
    "Program",
    "Degree Type",
    "Country",
    "City",
    "Department",
    "Duration",
    "Program Website",
    "Application Portal",
    "Research Tags",
    "Funding",
    "Funding Description",
    "Fully Funded",
    "Tuition Per Year (USD)",
    "Living Cost Per Month (USD)",
    "Monthly Stipend (USD)",
    "Annual Stipend (USD)",
    "Housing Included",
    "Research Assistantship Available",
    "Teaching Assistantship Available",
    "Industry Thesis Available",
    "GRE Required",
    "English Requirement",
    "Minimum GPA",
    "Research Experience Important",
    "Publications Important",
    "Contact PI Before Applying",
    "Interview Required",
    "Application Opens",
    "Priority Deadline",
    "Scholarship Deadline",
    "Funding Deadline",
    "Final Application Deadline",
    "Expected Open Month",
    "Expected Deadline Month",
    "Deadline Status",
    "Required Documents",
    "Research Fit Score (1-10)",
    "Funding Score (1-10)",
    "Prestige Score (1-10)",
    "Industry Opportunity Score (1-10)",
    "Admission Probability Score (1-10)",
    "Overall Score (1-10)",
    "Priority Tier",
    "Official Website",
    "Notes",
]


class MastersParser:
    """Parse masters program rows into calendar events."""

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
        university = clean_text(row.get("University"))
        program = clean_text(row.get("Program"))
        if not university and not program:
            # nothing meaningful to build titles from
            return []
        source_id = opportunity_id("masters", university, program)

        title_base = f"{university} {program}".strip()
        description = self._build_description(row)
        url = clean_text(row.get("Official Website")) or clean_text(row.get("Application Portal")) or None
        tags = split_tags(row.get("Research Tags"))
        category = None

        events: list[CalendarEvent] = []

        # date fields to produce events for
        mapping = [
            ("Application Opens", "Applications Open — {}", "application-open"),
            ("Priority Deadline", "Priority Deadline — {}", "priority-deadline"),
            ("Scholarship Deadline", "Scholarship Deadline — {}", "scholarship-deadline"),
            ("Funding Deadline", "Funding Deadline — {}", "funding-deadline"),
            ("Final Application Deadline", "Application Deadline — {}", "application-deadline"),
        ]

        for col, title_tpl, kind in mapping:
            dt = parse_exact_date(row.get(col))
            if dt:
                events.append(
                    self._event(
                        id=event_id(source_id, kind),
                        title=title_tpl.format(title_base),
                        start_date=dt,
                        description=description,
                        url=url,
                        category=category,
                        tags=tags,
                    )
                )

        has_exact_open = any(event.title.startswith("Applications Open —") for event in events)
        has_exact_deadline = parse_exact_date(row.get("Final Application Deadline")) is not None
        expected_open = parse_month_start(row.get("Expected Open Month")) if not has_exact_open else None
        if expected_open:
            events.append(
                self._event(
                    id=event_id(source_id, "application-open"),
                    title=f"Expected Applications Open — {title_base}",
                    start_date=expected_open,
                    description=description,
                    url=url,
                    category=category,
                    tags=tags,
                )
            )

        expected_deadline = (
            parse_month_start(
                row.get("Expected Deadline Month"),
                fallback_year=expected_open.year if expected_open else None,
            )
            if not has_exact_deadline
            else None
        )
        if expected_deadline:
            if expected_open and expected_deadline < expected_open:
                expected_deadline = expected_deadline.replace(year=expected_deadline.year + 1)
            events.append(
                self._event(
                    id=event_id(source_id, "application-deadline"),
                    title=f"Expected Application Deadline — {title_base}",
                    start_date=expected_deadline,
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
        id: str,
        title: str,
        start_date: date,
        description: str,
        url: str | None,
        category: str | None,
        tags: list[str],
    ) -> CalendarEvent:
        return CalendarEvent(
            id=id,
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
            ("University", "University"),
            ("Program", "Program"),
            ("Degree Type", "Degree Type"),
            ("Country", "Country"),
            ("City", "City"),
            ("Department", "Department"),
            ("Duration", "Duration"),
            ("Funding", "Funding"),
            ("Funding Description", "Funding Description"),
            ("Fully Funded", "Fully Funded"),
            ("Tuition Per Year (USD)", "Tuition Per Year (USD)"),
            ("Living Cost Per Month (USD)", "Living Cost Per Month (USD)"),
            ("Monthly Stipend (USD)", "Monthly Stipend (USD)"),
            ("Annual Stipend (USD)", "Annual Stipend (USD)"),
            ("Housing Included", "Housing Included"),
            ("Research Assistantship Available", "Research Assistantship Available"),
            ("Teaching Assistantship Available", "Teaching Assistantship Available"),
            ("Industry Thesis Available", "Industry Thesis Available"),
            ("GRE Required", "GRE Required"),
            ("English Requirement", "English Requirement"),
            ("Minimum GPA", "Minimum GPA"),
            ("Research Experience Important", "Research Experience Important"),
            ("Publications Important", "Publications Important"),
            ("Contact PI Before Applying", "Contact PI Before Applying"),
            ("Interview Required", "Interview Required"),
            ("Required Documents", "Required Documents"),
            ("Research Tags", "Research Tags"),
            ("Research Fit Score (1-10)", "Research Fit Score (1-10)"),
            ("Funding Score (1-10)", "Funding Score (1-10)"),
            ("Prestige Score (1-10)", "Prestige Score (1-10)"),
            ("Industry Opportunity Score (1-10)", "Industry Opportunity Score (1-10)"),
            ("Admission Probability Score (1-10)", "Admission Probability Score (1-10)"),
            ("Overall Score (1-10)", "Overall Score (1-10)"),
            ("Priority Tier", "Priority Tier"),
            ("Notes", "Notes"),
        ]

        for key, label in fields:
            value = clean_text(row.get(key))
            if value:
                lines.append(f"{label}: {value}")

        return join_non_empty_lines(lines)


def parse(csv_path: str | Path) -> list[CalendarEvent]:
    return MastersParser().parse(csv_path)
