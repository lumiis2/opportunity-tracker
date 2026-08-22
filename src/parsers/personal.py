"""Parser for a personal opportunity tracker spreadsheet."""

from __future__ import annotations

import csv
import re
from datetime import date, timedelta
from pathlib import Path

from src.core.calendar_event import CalendarEvent
from src.utils.date_helpers import clean_text, join_non_empty_lines, parse_exact_date


EXPECTED_COLUMNS = [
    "Programa", "Categoria", "Nível", "Instituição / organização", "Área / foco",
    "Local", "Formato", "Duração", "Applications open", "Deadline",
    "Período / data do programa", "Elegível?", "Requisitos / elegibilidade relevantes",
    "Funding / benefícios", "Seleção / docs relevantes", "Prioridade",
    "Status / observações", "Link", "Já apliquei?",
]

_MARKDOWN_LINK = re.compile(r"^\[([^]]+)]\((https?://[^)]+)\)$")
_RANGE = re.compile(
    r"(\d{4}[-/]\d{2}[-/]\d{2}|\d{2}/\d{2}/\d{4})\s*(?:a|até|to|–|—)\s*"
    r"(\d{4}[-/]\d{2}[-/]\d{2}|\d{2}/\d{2}/\d{4})",
    re.IGNORECASE,
)
_SEASONS = {"winter": 1, "spring": 3, "summer": 6, "fall": 9, "autumn": 9}


def _url(value: object) -> str | None:
    text = clean_text(value)
    match = _MARKDOWN_LINK.match(text)
    return (match.group(2) if match else text) or None


def _estimated_period(value: object) -> date | None:
    text = clean_text(value).lower()
    year_match = re.search(r"\b(20\d{2})\b", text)
    if not year_match:
        return None
    for season, month in _SEASONS.items():
        if season in text:
            return date(int(year_match.group(1)), month, 1)
    return None


class PersonalParser:
    """Turn personal tracker rows into application and program events."""

    def parse(self, csv_path: str | Path) -> list[CalendarEvent]:
        with Path(csv_path).open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            self._validate_columns(reader.fieldnames)
            return [event for row in reader for event in self._parse_row(row)]

    @staticmethod
    def _validate_columns(fieldnames: list[str] | None) -> None:
        if not fieldnames:
            raise ValueError("CSV file has no header row")
        missing = [column for column in EXPECTED_COLUMNS if column not in fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

    def _parse_row(self, row: dict[str, str]) -> list[CalendarEvent]:
        program = clean_text(row.get("Programa"))
        if not program:
            return []
        description = self._description(row)
        url = _url(row.get("Link"))
        category = clean_text(row.get("Categoria")) or None
        tags = [value for value in (clean_text(row.get("Nível")), clean_text(row.get("Prioridade"))) if value]
        events: list[CalendarEvent] = []

        opened = parse_exact_date(row.get("Applications open"))
        deadline = parse_exact_date(row.get("Deadline"))
        if opened:
            events.append(CalendarEvent(f"Applications Open — {program}", description, opened, url=url, category=category, tags=tags))
        if deadline:
            events.append(CalendarEvent(f"Application Deadline — {program}", description, deadline, url=url, category=category, tags=tags))

        period = clean_text(row.get("Período / data do programa"))
        match = _RANGE.search(period)
        if match:
            start, end = parse_exact_date(match.group(1)), parse_exact_date(match.group(2))
            if start and end:
                # DTEND is exclusive for all-day events.
                events.append(CalendarEvent(program, description, start, end + timedelta(days=1), url, category, tags))
        else:
            exact = parse_exact_date(period)
            estimated = _estimated_period(period) if not exact else None
            if exact:
                events.append(CalendarEvent(program, description, exact, url=url, category=category, tags=tags))
            elif estimated:
                events.append(CalendarEvent(f"Expected Program Period — {program}", description, estimated, url=url, category=category, tags=tags))
        return events

    @staticmethod
    def _description(row: dict[str, str]) -> str:
        excluded = {"Applications open", "Deadline", "Link"}
        return join_non_empty_lines(
            f"{column}: {clean_text(row.get(column))}"
            for column in EXPECTED_COLUMNS
            if column not in excluded and clean_text(row.get(column))
        )


def parse(csv_path: str | Path) -> list[CalendarEvent]:
    return PersonalParser().parse(csv_path)
