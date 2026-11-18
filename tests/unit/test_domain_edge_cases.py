from datetime import date

import pytest

from src.core import CalendarEvent, Milestone, Opportunity
from src.utils.date_helpers import resolve_date, resolve_window


def test_resolve_date_returns_none_when_both_values_are_unknown():
    assert resolve_date("TBD", "Unknown", fallback_year=2030) is None


def test_resolve_window_uses_exact_opening_year_for_estimated_deadline():
    _, deadline = resolve_window(
        open_value="2030-10-01",
        deadline_value="November",
        fallback_year=2027,
    )

    assert deadline is not None
    assert deadline.value == date(2030, 11, 1)
    assert deadline.estimated is True


def test_resolve_window_keeps_later_estimated_deadline_in_same_year():
    opening, deadline = resolve_window(
        open_value="September 2030",
        deadline_value="October",
    )

    assert opening is not None
    assert deadline is not None
    assert opening.value == date(2030, 9, 1)
    assert deadline.value == date(2030, 10, 1)
    assert deadline.estimated is True


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("tags", "AI"),
        ("milestones", Milestone("application-open", "Open", date(2030, 1, 1))),
    ],
)
def test_opportunities_do_not_share_default_collections(field, value):
    first = Opportunity("first", "masters", "First", "Description")
    second = Opportunity("second", "masters", "Second", "Description")

    getattr(first, field).append(value)

    assert getattr(second, field) == []


def test_calendar_events_do_not_share_default_tags():
    first = CalendarEvent("first", "First", "Description", date(2030, 1, 1))
    second = CalendarEvent("second", "Second", "Description", date(2030, 1, 1))

    first.tags.append("AI")

    assert second.tags == []
