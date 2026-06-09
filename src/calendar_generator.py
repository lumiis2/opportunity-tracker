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
) -> CalendarGenerationReport:
    """Build an ICS calendar and count created event types."""

    if reference_date is None:
        reference_date = date.today()

    events = []
    deadline_events = 0
    check_events = 0
    calendar = Calendar()
    for opportunity in opportunities:
        event, event_type = _build_event(opportunity, reference_date)
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


def _build_event(
    opportunity: Opportunity,
    reference_date: date,
) -> tuple[Optional[Event], str]:
    if opportunity.application_deadline is not None:
        return _build_deadline_event(opportunity), "deadline"

    if opportunity.expected_deadline_month is not None:
        return _build_expected_deadline_event(opportunity, reference_date), "check"

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


def _build_expected_deadline_event(opportunity: Opportunity, reference_date: date) -> Event:
    reminder_date = _expected_deadline_reminder_date(
        reference_date, opportunity.expected_deadline_month
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


def _expected_deadline_reminder_date(reference_date: date, expected_deadline_month: int) -> date:
    deadline_year = reference_date.year
    if expected_deadline_month < reference_date.month:
        deadline_year += 1

    if expected_deadline_month == 1:
        return date(deadline_year - 1, 12, 1)

    return date(deadline_year, expected_deadline_month - 1, 1)
