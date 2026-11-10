"""Core calendar domain objects and shared generation helpers."""

from src.core.calendar_event import CalendarEvent
from src.core.event_factory import create_calendar_events
from src.core.ics_generator import generate_calendar
from src.core.opportunity import Milestone, Opportunity

__all__ = [
    "CalendarEvent",
    "Milestone",
    "Opportunity",
    "create_calendar_events",
    "generate_calendar",
]
