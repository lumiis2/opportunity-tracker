from __future__ import annotations

from collections.abc import Callable
from datetime import date
from typing import Any, TypeVar

from ..domain.calendar_event import CalendarEvent
from ..domain.conference import Conference
from ..domain.graduation_opportunity import GraduationOpportunity
from ..domain.master_program import MasterProgram
from ..models import Opportunity as LegacyOpportunity

T = TypeVar("T")
Extractor = Callable[[Any, date | None, int], list[CalendarEvent]]
_EXTRACTORS: dict[type[Any], Extractor] = {}


def register_extractor(record_type: type[T]) -> Callable[[Extractor], Extractor]:
    def decorator(func: Extractor) -> Extractor:
        _EXTRACTORS[record_type] = func
        return func

    return decorator


def extract_calendar_events(record: Any, reference_date: date | None = None, lead_months: int = 1) -> list[CalendarEvent]:
    for record_type, extractor in _EXTRACTORS.items():
        if isinstance(record, record_type):
            return extractor(record, reference_date, lead_months)
    raise TypeError(f"No extractor registered for {type(record)!r}")


from .conference_event_extractor import extract_conference_events  # noqa: E402
from .graduation_event_extractor import extract_graduation_events  # noqa: E402
from .legacy_opportunity_extractor import extract_legacy_opportunity_events  # noqa: E402
from .master_program_event_extractor import extract_master_program_events  # noqa: E402

__all__ = [
    "extract_calendar_events",
    "extract_conference_events",
    "extract_graduation_events",
    "extract_legacy_opportunity_events",
    "extract_master_program_events",
    "register_extractor",
]
