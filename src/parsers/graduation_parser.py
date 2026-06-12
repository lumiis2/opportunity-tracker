from __future__ import annotations

from pathlib import Path

from ..domain.graduation_opportunity import GraduationOpportunity
from .common import first_month_from_text, parse_iso_date, read_rows, text_or_none


def parse_graduation_opportunities(csv_path: Path) -> list[GraduationOpportunity]:
    rows = read_rows(csv_path)
    opportunities: list[GraduationOpportunity] = []

    for row in rows:
        normalized = {
            "category": row.get("Category"),
            "subcategory": row.get("Subcategory"),
            "program": row.get("Program"),
            "organization": row.get("Organization"),
            "host_institution": row.get("Host Institution"),
            "country": row.get("Country"),
            "career_stage": row.get("Career Stage"),
            "funding_type": row.get("Funding Type"),
            "funding_details": row.get("Funding Details"),
            "duration": row.get("Duration"),
            "application_open": parse_iso_date(row.get("Application Open")),
            "application_deadline": parse_iso_date(row.get("Application Deadline")),
            "expected_open_month": first_month_from_text([row.get("Expected Open Month"), row.get("Application Open")]),
            "expected_deadline_month": first_month_from_text([row.get("Expected Deadline Month"), row.get("Application Deadline")]),
            "date_status": text_or_none(row.get("Date Status")) or "unknown",
            "deadline_confidence": text_or_none(row.get("Deadline Confidence")) or "low",
            "application_effort": row.get("Application Effort"),
            "prestige_score": row.get("Prestige Score (1-10)"),
            "funding_score": row.get("Funding Score (1-10)"),
            "fit_score": row.get("Fit Score for AI/ML Student (1-10)"),
            "official_website": row.get("Official Website"),
            "notes": row.get("Notes"),
            "raw": row,
        }
        opportunities.append(GraduationOpportunity.model_validate(normalized))

    return opportunities
