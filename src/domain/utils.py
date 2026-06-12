from __future__ import annotations

from calendar import month_name
from datetime import date

_MONTH_LOOKUP = {month_name[index].lower(): index for index in range(1, 13)}


def parse_month_value(value: object) -> int | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    if text.isdigit():
        month = int(text)
        return month if 1 <= month <= 12 else None
    return _MONTH_LOOKUP.get(text)


def reminder_date_for_month(expected_deadline_month: int, reference_date: date | None = None, lead_months: int = 1) -> date:
    if lead_months < 0:
        raise ValueError("lead_months must be >= 0")

    if reference_date is None:
        reference_date = date.today()

    deadline_year = reference_date.year
    if expected_deadline_month < reference_date.month:
        deadline_year += 1

    abs_month = deadline_year * 12 + (expected_deadline_month - 1)
    reminder_abs = abs_month - lead_months
    reminder_year = reminder_abs // 12
    reminder_month = (reminder_abs % 12) + 1
    return date(reminder_year, reminder_month, 1)
