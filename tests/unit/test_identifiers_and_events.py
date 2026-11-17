from datetime import date

import pytest

from src.core import CalendarEvent, Milestone, Opportunity, create_calendar_events
from src.utils.identifiers import opportunity_id


def test_opportunity_id_normalizes_accents_and_uppercase():
    result = opportunity_id("masters", "Mestrado São Paulo")

    assert result == "masters-mestrado-sao-paulo"


def test_opportunity_id_collapses_punctuation_into_separators():
    result = opportunity_id("industry", "  Research & Development / AI!  ")

    assert result == "industry-research-development-ai"


def test_opportunity_id_ignores_missing_name_parts():
    result = opportunity_id("masters", "Example", None, "", "   ", "AI")

    assert result == "masters-example-ai"


@pytest.mark.parametrize("name", [None, "", "   ", "!!!"])
def test_opportunity_id_rejects_names_without_usable_characters(name):
    with pytest.raises(ValueError, match="without a name"):
        opportunity_id("masters", name)


def test_opportunity_id_distinguishes_tracks_with_the_same_name():
    masters_id = opportunity_id("masters", "AI")
    industry_id = opportunity_id("industry", "AI")

    assert masters_id != industry_id


def test_create_calendar_events_returns_empty_list_for_empty_input():
    assert create_calendar_events([]) == []


def test_create_calendar_events_skips_opportunities_without_milestones():
    undated = Opportunity("masters-undated", "masters", "Undated", "No dates")
    dated = Opportunity(
        "masters-dated",
        "masters",
        "Dated",
        "Has a deadline",
        milestones=[
            Milestone("application-deadline", "Deadline", date(2027, 2, 1)),
        ],
    )

    result = create_calendar_events([undated, dated])

    assert [event.id for event in result] == [
        "masters-dated.application-deadline",
    ]


def test_create_calendar_events_preserves_milestone_and_opportunity_details():
    opportunity = Opportunity(
        id="masters-example",
        track="masters",
        title="Example Program",
        description="Fully funded program",
        url="https://example.org/program",
        category="Scholarship",
        tags=["AI", "Research"],
        milestones=[
            Milestone(
                "program-period",
                "Research period",
                date(2027, 9, 1),
                date(2027, 12, 1),
            ),
        ],
    )

    result = create_calendar_events([opportunity])

    assert result == [
        CalendarEvent(
            id="masters-example.program-period",
            title="Research period",
            description="Fully funded program",
            start_date=date(2027, 9, 1),
            end_date=date(2027, 12, 1),
            url="https://example.org/program",
            category="Scholarship",
            tags=["AI", "Research"],
        ),
    ]


def test_create_calendar_events_creates_one_event_per_milestone():
    opportunity = Opportunity(
        "masters-example",
        "masters",
        "Example",
        "Description",
        milestones=[
            Milestone("application-open", "Applications open", date(2027, 1, 1)),
            Milestone("application-deadline", "Deadline", date(2027, 2, 1)),
        ],
    )

    result = create_calendar_events([opportunity])

    assert [(event.id, event.start_date) for event in result] == [
        ("masters-example.application-open", date(2027, 1, 1)),
        ("masters-example.application-deadline", date(2027, 2, 1)),
    ]


def test_create_calendar_events_separates_same_kind_between_opportunities():
    first = Opportunity(
        "masters-first",
        "masters",
        "First",
        "First program",
        milestones=[
            Milestone("application-deadline", "Deadline", date(2027, 2, 1)),
        ],
    )
    second = Opportunity(
        "masters-second",
        "masters",
        "Second",
        "Second program",
        milestones=[
            Milestone("application-deadline", "Deadline", date(2027, 2, 1)),
        ],
    )

    result = create_calendar_events([first, second])

    assert [(event.id, event.description) for event in result] == [
        ("masters-first.application-deadline", "First program"),
        ("masters-second.application-deadline", "Second program"),
    ]