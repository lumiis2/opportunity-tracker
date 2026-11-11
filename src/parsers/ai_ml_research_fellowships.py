"""Parser for the AI/ML Research & Fellowships dataset."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import csv
import re

from src.core import Milestone, Opportunity
from src.utils.date_helpers import clean_text, join_non_empty_lines, resolve_window
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

    def parse(self, csv_path: str | Path) -> list[Opportunity]:
        with Path(csv_path).open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            self._validate_columns(reader.fieldnames)
            return [opportunity for row in reader if (opportunity := self._parse_row(row))]

    @staticmethod
    def _validate_columns(fieldnames: list[str] | None) -> None:
        if not fieldnames:
            raise ValueError("CSV file has no header row")
        missing = [column for column in EXPECTED_COLUMNS if column not in fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

    def _parse_row(self, row: dict[str, str]) -> Opportunity | None:
        program = _link_label(row.get("Program"))
        if not program:
            return None
        source_id = opportunity_id("ai-ml", program, row.get("Organization"))

        category = clean_text(row.get("Category")) or None
        subcategory = clean_text(row.get("Subcategory"))
        tags = [subcategory] if subcategory else []
        description = self._build_description(row)
        url = _link_url(row.get("Official Website")) or None
        opening, deadline = resolve_window(
            open_value=row.get("Application Open"),
            deadline_value=row.get("Application Deadline"),
            expected_open=row.get("Expected Open Month"),
            expected_deadline=row.get("Expected Deadline Month"),
        )
        milestones = []
        if opening:
            milestones.append(Milestone("application-open", f"{'Expected ' if opening.estimated else ''}Applications Open — {program}", opening.value, estimated=opening.estimated))
        if deadline:
            milestones.append(Milestone("application-deadline", f"{'Expected ' if deadline.estimated else ''}Application Deadline — {program}", deadline.value, estimated=deadline.estimated))
        if not milestones and self._is_continuous(row):
            milestones.append(Milestone("continuous-applications", f"Applications Open Continuously — {program}", date(date.today().year, 1, 1)))

        return Opportunity(source_id, "ai_ml_research_fellowships", program, description, url, category, tags, milestones)

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


def parse(csv_path: str | Path) -> list[Opportunity]:
    return AiMlResearchFellowshipsParser().parse(csv_path)
