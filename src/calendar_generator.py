from __future__ import annotations

from dataclasses import dataclass
from calendar import month_name
from datetime import date
from pathlib import Path
from typing import Iterable, Optional

from ics import Calendar, Event

from .models import Opportunity


@dataclass(frozen=True)
class CalendarGenerationReport:
    """Summary of a generated calendar."""

    calendar: Calendar
    deadline_events: int
    check_events: int


def build_calendar(
    opportunities: Iterable[Opportunity],
    reference_date: Optional[date] = None,
) -> Calendar:
    """Build an ICS calendar from validated opportunities."""

    return build_calendar_report(opportunities, reference_date=reference_date).calendar


def build_calendar_report(
    opportunities: Iterable[Opportunity],
    reference_date: Optional[date] = None,
    lead_months: int = 1,
) -> CalendarGenerationReport:
    """Build an ICS calendar and count created event types."""

    if reference_date is None:
        reference_date = date.today()

    if lead_months < 0:
        raise ValueError("lead_months must be >= 0")

    events = []
    deadline_events = 0
    check_events = 0
    calendar = Calendar()
    for opportunity in opportunities:
        event, event_type = _build_event(opportunity, reference_date, lead_months=lead_months)
        if event is not None:
            events.append(event)
            if event_type == "deadline":
                deadline_events += 1
            elif event_type == "check":
                check_events += 1

    calendar.events = events

    return CalendarGenerationReport(
        calendar=calendar,
        deadline_events=deadline_events,
        check_events=check_events,
    )


def generate_calendar(
    opportunities: Iterable[Opportunity],
    output_path: Path,
    reference_date: Optional[date] = None,
) -> Path:
    """Generate an ICS file from validated opportunities.

    The output directory is created automatically.
    """

    report = build_calendar_report(opportunities, reference_date=reference_date)
    return save_calendar(report.calendar, output_path)


def save_calendar(calendar: Calendar, output_path: Path) -> Path:
    """Persist a calendar to an ICS file."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(calendar.serialize(), encoding="utf-8")
    return output_path


def process_dataset(csv_path: Path, output_path: Path, lead_months: int = 1) -> tuple[int, int, int]:
    """Parse a CSV file, build a calendar and save it.

    Returns a tuple `(loaded_count, deadline_events, check_events)`.
    The function is resilient: if the CSV is empty it still writes an empty calendar.
    """

    from .parser import parse_opportunities

    opportunities = parse_opportunities(csv_path) if csv_path.exists() else []
    report = build_calendar_report(opportunities, lead_months=lead_months)
    save_calendar(report.calendar, output_path)
    return len(opportunities), report.deadline_events, report.check_events


def process_all(registry: dict[Path, Path], lead_months: int = 1) -> dict[Path, tuple[int, int, int]]:
    """Process every dataset in `registry`.

    Returns a mapping from output path -> stats tuple as returned by `process_dataset`.
    Continues processing on errors and records zero counts for missing inputs.
    """

    results: dict[Path, tuple[int, int, int]] = {}
    for csv_path, output_path in registry.items():
        try:
            loaded, dl, ch = process_dataset(csv_path, output_path, lead_months=lead_months)
        except Exception:
            # On any error, write an empty calendar so consumers have a file.
            save_calendar(Calendar(), output_path)
            results[output_path] = (0, 0, 0)
        else:
            results[output_path] = (loaded, dl, ch)

    return results


def _build_event(
    opportunity: Opportunity,
    reference_date: date,
    lead_months: int = 1,
) -> tuple[Optional[Event], str]:
    if opportunity.application_deadline is not None:
        return _build_deadline_event(opportunity), "deadline"

    if opportunity.expected_deadline_month is not None:
        return _build_expected_deadline_event(opportunity, reference_date, lead_months=lead_months), "check"

    return None, "ignored"


def _build_deadline_event(opportunity: Opportunity) -> Event:
    description = "\n".join(
        [
            opportunity.organization,
            opportunity.country,
            opportunity.official_website or "",
        ]
    )
    event = Event(f"🚨 {opportunity.program} Deadline")
    event.begin = opportunity.application_deadline
    event.description = description
    event.make_all_day()
    return event


def _build_expected_deadline_event(opportunity: Opportunity, reference_date: date, lead_months: int = 1) -> Event:
    reminder_date = _expected_deadline_reminder_date(
        reference_date, opportunity.expected_deadline_month, lead_months=lead_months
    )
    deadline_month_name = month_name[opportunity.expected_deadline_month]
    event = Event(f"🔍 Check {opportunity.program}")
    event.begin = reminder_date
    event.description = "\n".join(
        [
            "Expected deadline month:",
            deadline_month_name,
            "",
            "Verify official dates.",
        ]
    )
    event.make_all_day()
    return event


def _expected_deadline_reminder_date(reference_date: date, expected_deadline_month: int, lead_months: int = 1) -> date:
    """Return the date (first day) to remind the user before an expected deadline.

    The reminder is placed on the first day of the month that is `lead_months`
    before the expected deadline month. `lead_months=0` returns the first day
    of the expected deadline month.
    """

    if lead_months < 0:
        raise ValueError("lead_months must be >= 0")

    # Determine the year for the expected deadline (could be next year)
    deadline_year = reference_date.year
    if expected_deadline_month < reference_date.month:
        deadline_year += 1

    # Convert to absolute month index (zero-based) to make arithmetic simple
    abs_month = deadline_year * 12 + (expected_deadline_month - 1)
    reminder_abs = abs_month - lead_months
    reminder_year = reminder_abs // 12
    reminder_month = (reminder_abs % 12) + 1

    return date(reminder_year, reminder_month, 1)
