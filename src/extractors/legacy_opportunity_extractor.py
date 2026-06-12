from __future__ import annotations

from datetime import date

from ..domain.calendar_event import CalendarEvent
from ...models import Opportunity as LegacyOpportunity
from . import register_extractor


@register_extractor(LegacyOpportunity)
def extract_legacy_opportunity_events(opportunity: LegacyOpportunity, reference_date: date | None = None, lead_months: int = 1) -> list[CalendarEvent]:
    """Compatibility extractor for the legacy shared model."""

    events: list[CalendarEvent] = []

    if opportunity.application_deadline is not None:
        events.append(
            CalendarEvent(
                title=f"🚨 {opportunity.program} Deadline",
                start_date=opportunity.application_deadline,
                description="\n".join(
                    [
                        opportunity.organization,
                        opportunity.country,
                        opportunity.official_website or "",
                    ]
                ).strip(),
                url=opportunity.official_website,
            )
        )
        return events

    if opportunity.expected_deadline_month is not None:
        from ..domain.utils import reminder_date_for_month

        events.append(
            CalendarEvent(
                title=f"🔍 Check {opportunity.program}",
                start_date=reminder_date_for_month(
                    opportunity.expected_deadline_month,
                    reference_date=reference_date,
                    lead_months=lead_months,
                ),
                description="\n".join(
                    [
                        f"Organization: {opportunity.organization}",
                        f"Expected deadline month: {opportunity.expected_deadline_month}",
                        "Verify official dates.",
                    ]
                ).strip(),
                url=opportunity.official_website,
            )
        )

    return events
