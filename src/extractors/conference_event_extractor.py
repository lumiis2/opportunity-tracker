from __future__ import annotations

from datetime import date

from ..domain.calendar_event import CalendarEvent
from ..domain.conference import Conference
from . import register_extractor


@register_extractor(Conference)
def extract_conference_events(conference: Conference, reference_date: date | None = None, lead_months: int = 1) -> list[CalendarEvent]:
    return conference.to_calendar_events(reference_date=reference_date, lead_months=lead_months)
