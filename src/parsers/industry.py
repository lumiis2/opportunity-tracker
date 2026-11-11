"""Parser for the Industry Opportunities dataset."""

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

    def parse(self, csv_path: str | Path) -> list[Opportunity]:
        path = Path(csv_path)
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            self._validate_columns(reader.fieldnames)

            return [opportunity for row in reader if (opportunity := self._parse_row(row))]

    def _validate_columns(self, fieldnames: list[str] | None) -> None:
        if not fieldnames:
            raise ValueError("CSV file has no header row")
        missing = [name for name in EXPECTED_COLUMNS if name not in fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

    def _parse_row(self, row: dict[str, str]) -> Opportunity | None:
        company = clean_text(row.get("Company"))
        category = clean_text(row.get("Category")) or None
        program_name = company
        if not program_name:
            return None
        source_id = opportunity_id("industry", company)

        title_base = f"{program_name}".strip()
        description = self._build_description(row)
        url = clean_text(row.get("Careers Page")) or clean_text(row.get("Application Portal")) or None

        tags = []
        tags.extend(split_tags(row.get("Primary Focus")))
        tags.extend(split_tags(row.get("Main Domains")))

        opening, deadline = resolve_window(
            open_value=row.get("Applications Open"),
            deadline_value=row.get("Application Deadline"),
            expected_open=row.get("Expected Open Month"),
            expected_deadline=row.get("Expected Deadline Month"),
        )
        milestones = []
        if opening:
            milestones.append(Milestone("application-open", f"{'Expected ' if opening.estimated else ''}Applications Open — {title_base}", opening.value, estimated=opening.estimated))
        if deadline:
            milestones.append(Milestone("application-deadline", f"{'Expected ' if deadline.estimated else ''}Application Deadline — {title_base}", deadline.value, estimated=deadline.estimated))

        return Opportunity(source_id, "industry", title_base, description, url, category, tags, milestones)

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


def parse(csv_path: str | Path) -> list[Opportunity]:
    return IndustryParser().parse(csv_path)
