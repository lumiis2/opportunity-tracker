"""Parser for the Conferences dataset."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path
import csv
import re

from src.core import Milestone, Opportunity
from src.utils.date_helpers import (
    clean_text,
    join_non_empty_lines,
    parse_exact_date,
    parse_month_start,
    split_tags,
)
from src.utils.identifiers import opportunity_id


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

    def parse(self, csv_path: str | Path) -> list[Opportunity]:
        path = Path(csv_path)
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
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
        name = clean_text(row.get("Conference Name"))
        if not name:
            return None
        source_id = opportunity_id("conference", name, row.get("Organizer / Association"))

        area = clean_text(row.get("Area"))
        research_tags = split_tags(row.get("Research Tags"))
        tags = []
        if area:
            tags.append(area)
        tags.extend(research_tags)

        description = self._build_description(row)
        url = clean_text(row.get("Submission Portal")) or clean_text(row.get("Website")) or None

        milestones: list[Milestone] = []

        # Submission deadline (exact)
        sub_dead = parse_exact_date(row.get("Submission Deadline (Exact or Empty if unknown)"))
        if sub_dead:
            milestones.append(Milestone("submission-deadline", f"Paper Submission Deadline — {name}", sub_dead))

        # Expected submission month
        expected_sub = parse_month_start(row.get("Expected Submission Month"))
        if expected_sub and not sub_dead:
            milestones.append(Milestone("submission-deadline", f"Expected Paper Submission — {name}", expected_sub, estimated=True))

        # Notification date
        notif = parse_exact_date(row.get("Notification Date"))
        if notif:
            milestones.append(Milestone("notification", f"Acceptance Notification — {name}", notif))

        # Conference date range: format "YYYY-MM-DD to YYYY-MM-DD"
        rng = clean_text(row.get("Conference Date Range"))
        if rng:
            m = re.search(r"(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})", rng)
            if m:
                start = parse_exact_date(m.group(1))
                end = parse_exact_date(m.group(2))
                if start and end:
                    milestones.append(Milestone("conference-period", f"{name} Conference", start, end + timedelta(days=1)))

        return Opportunity(source_id, "conferences", name, description, url, area or None, tags, milestones)

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


def parse(csv_path: str | Path) -> list[Opportunity]:
    return ConferenceParser().parse(csv_path)
