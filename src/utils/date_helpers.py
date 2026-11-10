"""Small helpers for parsing dates and cleaning text fields."""

from __future__ import annotations

from dataclasses import dataclass
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


@dataclass(frozen=True, slots=True)
class ResolvedDate:
    """A parsed date and whether it came from an estimated month."""

    value: date
    estimated: bool


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


def resolve_date(
    exact_value: object,
    expected_value: object = None,
    fallback_year: int | None = None,
) -> ResolvedDate | None:
    """Prefer an exact date and otherwise resolve an estimated month."""

    exact = parse_exact_date(exact_value)
    if exact:
        return ResolvedDate(exact, estimated=False)

    estimated = parse_month_start(exact_value, fallback_year) or parse_month_start(
        expected_value, fallback_year
    )
    return ResolvedDate(estimated, estimated=True) if estimated else None


def resolve_window(
    *,
    open_value: object,
    deadline_value: object,
    expected_open: object = None,
    expected_deadline: object = None,
    fallback_year: int | None = None,
) -> tuple[ResolvedDate | None, ResolvedDate | None]:
    """Resolve an opening and deadline, including estimated cross-year windows."""

    opening = resolve_date(open_value, expected_open, fallback_year)
    deadline_year = opening.value.year if opening else fallback_year
    deadline = resolve_date(deadline_value, expected_deadline, deadline_year)

    if opening and deadline and deadline.estimated and deadline.value < opening.value:
        deadline = ResolvedDate(
            deadline.value.replace(year=deadline.value.year + 1),
            estimated=True,
        )

    return opening, deadline


def join_non_empty_lines(lines: Iterable[str]) -> str:
    return "\n".join(line for line in lines if line)
