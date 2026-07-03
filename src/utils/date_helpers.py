"""Small helpers for parsing dates and cleaning text fields."""

from __future__ import annotations

from datetime import date, datetime
import re
from typing import Iterable


_MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def clean_text(value: object) -> str:
    """Return a stripped string or an empty string for null-like values."""

    if value is None:
        return ""
    text = str(value).strip()
    return "" if text in {"", "nan", "None"} else text


def is_blank(value: object) -> bool:
    return clean_text(value) == ""


def split_tags(value: object) -> list[str]:
    """Split a tags field into a clean list of strings."""

    text = clean_text(value)
    if not text:
        return []

    parts = re.split(r"[,;/|]", text)
    tags = [part.strip() for part in parts if part.strip()]
    return tags


def parse_exact_date(value: object) -> date | None:
    """Parse a fully specified date value such as YYYY-MM-DD."""

    text = clean_text(value)
    if not text:
        return None

    match = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", text)
    if match:
        try:
            return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            return None

    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def parse_month_start(value: object, fallback_year: int | None = None) -> date | None:
    """Parse a month name or month/year string into the first day of that month."""

    text = clean_text(value)
    if not text:
        return None

    lower = text.lower()
    year = fallback_year or date.today().year

    year_match = re.search(r"\b(20\d{2})\b", lower)
    if year_match:
        year = int(year_match.group(1))

    month = None
    for name, number in _MONTHS.items():
        if name in lower:
            month = number
            break

    if month is None:
        return None

    return date(year, month, 1)


def join_non_empty_lines(lines: Iterable[str]) -> str:
    return "\n".join(line for line in lines if line)
