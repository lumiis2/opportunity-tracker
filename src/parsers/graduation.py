"""Parser for the Graduation Opportunities dataset."""

from __future__ import annotations

from pathlib import Path
import csv

from src.core import Milestone, Opportunity
from src.utils.date_helpers import (
    clean_text,
    join_non_empty_lines,
    resolve_window,
    split_tags,
)
from src.utils.identifiers import opportunity_id


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
    """Parse graduation CSV rows into normalized opportunities."""

    def parse(self, csv_path: str | Path) -> list[Opportunity]:
        path = Path(csv_path)
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            self._validate_columns(reader.fieldnames)

            return [self._parse_row(row) for row in reader]

    def _validate_columns(self, fieldnames: list[str] | None) -> None:
        if not fieldnames:
            raise ValueError("CSV file has no header row")

        missing = [name for name in EXPECTED_COLUMNS if name not in fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

    def _parse_row(self, row: dict[str, str]) -> Opportunity:
        program = clean_text(row.get("Program"))
        if not program:
            raise ValueError("Missing Program value in row")
        source_id = opportunity_id("graduation", program, row.get("Organization"))

        description = self._build_description(row)
        category = clean_text(row.get("Category")) or None
        url = clean_text(row.get("Official Website")) or clean_text(row.get("Application Portal")) or None
        tags = split_tags(row.get("Tags"))

        opening, deadline = resolve_window(
            open_value=row.get("Application Open"),
            deadline_value=row.get("Application Deadline"),
            expected_open=row.get("Expected Open Month"),
            expected_deadline=row.get("Expected Deadline Month"),
        )
        milestones = []
        if opening:
            opening_title = (
                f"Expected Applications Open — {program}"
                if opening.estimated
                else f"Application Opens — {program}"
            )
            milestones.append(
                Milestone(
                    "application-open",
                    opening_title,
                    opening.value,
                    estimated=opening.estimated,
                )
            )
        if deadline:
            milestones.append(Milestone("application-deadline", f"{'Expected ' if deadline.estimated else ''}Application Deadline — {program}", deadline.value, estimated=deadline.estimated))

        return Opportunity(source_id, "graduation", program, description, url, category, tags, milestones)

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


def parse(csv_path: str | Path) -> list[Opportunity]:
    """Parse a graduation CSV into opportunities."""

    return GraduationParser().parse(csv_path)
