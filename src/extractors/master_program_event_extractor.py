from __future__ import annotations

from datetime import date

from ..domain.calendar_event import CalendarEvent
from ..domain.master_program import MasterProgram
from . import register_extractor


@register_extractor(MasterProgram)
def extract_master_program_events(program: MasterProgram, reference_date: date | None = None, lead_months: int = 1) -> list[CalendarEvent]:
    return program.to_calendar_events(reference_date=reference_date, lead_months=lead_months)
