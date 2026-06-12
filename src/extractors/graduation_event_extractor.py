from __future__ import annotations

from datetime import date

from ..domain.calendar_event import CalendarEvent
from ..domain.graduation_opportunity import GraduationOpportunity
from . import register_extractor


@register_extractor(GraduationOpportunity)
def extract_graduation_events(opportunity: GraduationOpportunity, reference_date: date | None = None, lead_months: int = 1) -> list[CalendarEvent]:
    return opportunity.to_calendar_events(reference_date=reference_date, lead_months=lead_months)
