"""Parser for the Master Programs dataset."""

from __future__ import annotations

from pathlib import Path
import csv

from src.core import Milestone, Opportunity
from src.utils.date_helpers import (
    clean_text,
    join_non_empty_lines,
    parse_exact_date,
    resolve_window,
    split_tags,
)
from src.utils.identifiers import opportunity_id


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
        university = clean_text(row.get("University"))
        program = clean_text(row.get("Program"))
        if not university and not program:
            # nothing meaningful to build titles from
            return None
        source_id = opportunity_id("masters", university, program)

        title_base = f"{university} {program}".strip()
        description = self._build_description(row)
        url = clean_text(row.get("Official Website")) or clean_text(row.get("Application Portal")) or None
        tags = split_tags(row.get("Research Tags"))
        category = None

        milestones: list[Milestone] = []

        # date fields to produce events for
        mapping = [
            ("Priority Deadline", "Priority Deadline — {}", "priority-deadline"),
            ("Scholarship Deadline", "Scholarship Deadline — {}", "scholarship-deadline"),
            ("Funding Deadline", "Funding Deadline — {}", "funding-deadline"),
            ("Final Application Deadline", "Application Deadline — {}", "application-deadline"),
        ]

        for col, title_tpl, kind in mapping:
            dt = parse_exact_date(row.get(col))
            if dt:
                milestones.append(Milestone(kind, title_tpl.format(title_base), dt))

        opening, deadline = resolve_window(
            open_value=row.get("Application Opens"),
            deadline_value=(
                row.get("Final Application Deadline")
                if parse_exact_date(row.get("Final Application Deadline"))
                else None
            ),
            expected_open=row.get("Expected Open Month"),
            expected_deadline=row.get("Expected Deadline Month"),
        )
        if opening:
            milestones.append(Milestone("application-open", f"{'Expected ' if opening.estimated else ''}Applications Open — {title_base}", opening.value, estimated=opening.estimated))
        if deadline:
            milestones.append(Milestone("application-deadline", f"{'Expected ' if deadline.estimated else ''}Application Deadline — {title_base}", deadline.value, estimated=deadline.estimated))

        return Opportunity(source_id, "masters", title_base, description, url, category, tags, milestones)

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


def parse(csv_path: str | Path) -> list[Opportunity]:
    return MastersParser().parse(csv_path)
