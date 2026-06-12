from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from ..domain.master_program import MasterProgram
from .common import first_month_from_text, parse_iso_date, read_rows, text_or_none


def _parse_optional_int(value: Any) -> int | None:
    text = text_or_none(value)
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def parse_master_programs(csv_path: Path) -> list[MasterProgram]:
    rows = read_rows(csv_path)
    programs: list[MasterProgram] = []

    for row in rows:
        normalized = {
            "program_id": row.get("Program_ID"),
            "university": row.get("University"),
            "program": row.get("Program"),
            "degree_type": row.get("Degree_Type"),
            "country": row.get("Country"),
            "city": row.get("City"),
            "department": row.get("Department"),
            "duration": row.get("Duration"),
            "program_website": row.get("Program_Website"),
            "research_areas": row.get("Research_Areas"),
            "funding_type": row.get("Funding_Type"),
            "funding_description": row.get("Funding_Description"),
            "application_open": parse_iso_date(row.get("Application_Opens")),
            "application_deadline": parse_iso_date(row.get("Final_Application_Deadline"))
            or parse_iso_date(row.get("Priority_Deadline"))
            or parse_iso_date(row.get("Scholarship_Deadline"))
            or parse_iso_date(row.get("Funding_Deadline")),
            "expected_open_month": first_month_from_text([row.get("Application_Opens"), row.get("Program_Start_Date")]),
            "expected_deadline_month": first_month_from_text(
                [
                    row.get("Priority_Deadline"),
                    row.get("Scholarship_Deadline"),
                    row.get("Funding_Deadline"),
                    row.get("Final_Application_Deadline"),
                    row.get("Deadline_Status"),
                ]
            ),
            "deadline_status": row.get("Deadline_Status"),
            "notes": row.get("Notes"),
            "raw": row,
        }
        programs.append(MasterProgram.model_validate(normalized))

    return programs
