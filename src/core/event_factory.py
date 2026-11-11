"""Convert normalized opportunities into calendar events."""

from src.core.calendar_event import CalendarEvent
from src.core.opportunity import Opportunity
from src.utils.identifiers import event_id


def create_calendar_events(opportunities: list[Opportunity]) -> list[CalendarEvent]:
    return [
        CalendarEvent(
            id=event_id(opportunity.id, milestone.kind),
            title=milestone.title,
            description=opportunity.description,
            start_date=milestone.start_date,
            end_date=milestone.end_date,
            url=opportunity.url,
            category=opportunity.category,
            tags=opportunity.tags,
        )
        for opportunity in opportunities
        for milestone in opportunity.milestones
    ]
